"""
File browser routes for EFS Navigator application with pagination support.

This module implements the core file browsing functionality, including paginated directory
navigation, file viewing, downloading, and metadata retrieval. All routes are
secured with authentication and implement path traversal protection.
"""

import os
import mimetypes
import html
from flask import Blueprint, request, abort, send_file, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.browser.utils import get_mount_base, list_directory_paginated, safe_join, resolve_path, safe_listdir

# Create the browser blueprint for organizing routes
browser_bp = Blueprint('browser', __name__)

# Register common but missing MIME types
mimetypes.add_type('application/x-yaml', '.yaml')
mimetypes.add_type('application/x-yaml', '.yml')
mimetypes.add_type('text/plain', 'dockerfile')
mimetypes.add_type('text/x-jsp', '.jsp')

# Define MIME types that are safe to display in the browser
# These file types can be viewed directly without downloading
SAFE_MIME_TYPES = {
    'text/plain',
    'application/json',
    'application/xml',
    'application/javascript',
    'text/javascript',
    'text/css',
    'text/html',
    'application/x-sh',
    'text/markdown',
    'application/x-yaml',
    'text/yaml',
    'text/x-python',
    'application/x-python',
    'text/x-python-script',
    'application/x-msdownload',
    'text/x-java-source',
    'text/x-jsp',
    'application/x-jsp'
}

# Mapping of file extensions to Prism.js language identifiers for syntax highlighting
EXTENSION_TO_PRISM = {
    '.py':   'python',
    '.sh':   'bash',
    '.js':   'javascript',
    '.json': 'json',
    '.html': 'html',
    '.css':  'css',
    '.md':   'markdown',
    '.txt':  'none',
    '.yml':  'yaml',
    '.yaml': 'yaml',
    '.conf': 'none',
    '.ini':  'none',
    '.log':  'none',
    '.dockerfile': 'none',
    '.bat': 'powershell',
    '.java':    'java',
    '.jsp': 'html'
}

@browser_bp.route('/browse/<mount_id>', defaults={'subpath': ''}, strict_slashes=False)
@browser_bp.route('/browse/<mount_id>/<path:subpath>', strict_slashes=False)
@login_required
def browse(mount_id, subpath):
    """
    Browse directories and files within a mount's mount point with pagination support.
    
    This route handles directory navigation within mount-specific mount points.
    It displays paginated directory contents in a file browser interface and automatically
    redirects to the file viewer for individual files.
        
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 100, max: 500)
        sort: Sort field ('name', 'size', 'modified', 'type')
        desc: Sort descending if present
        
    Example URLs:
        /browse/mount-a                    # Mount root directory
        /browse/mount-a?page=2             # Second page
        /browse/mount-a/documents?per_page=50  # 50 items per page
        /browse/mount-a/files/config.json  # Redirects to file viewer
    """

    base_path = get_mount_base()

    # Combine mount_id and subpath for the full path
    full_subpath = os.path.join(mount_id, subpath) if subpath else mount_id
    full_path = safe_join(base_path, full_subpath)

    # Verify the requested path exists
    if not os.path.exists(full_path):
        current_app.logger.warning(f'[browse] Path not found: {full_path} (user: {current_user.id})')
        abort(404)

    # If the path is a file, redirect to the file viewer
    if os.path.isfile(full_path):
        return redirect(url_for('browser.view_file', mount_id=mount_id, subpath=subpath))

    # Get pagination parameters from query string
    try:
        page = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
        
    try:
        per_page = min(500, max(10, int(request.args.get('per_page', 100))))
    except (ValueError, TypeError):
        per_page = 100
        
    sort_by = request.args.get('sort', 'name')
    if sort_by not in ['name', 'size', 'modified', 'type']:
        sort_by = 'name'
        
    sort_desc = 'desc' in request.args

    try:
        # Get paginated directory contents with metadata
        result = list_directory_paginated(
            directory=full_path,
            mount_id=mount_id,
            base_subpath=subpath,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        
        current_app.logger.info(
            f'[browse] User {current_user.id} accessed directory: {full_path} '
            f'(page {result["pagination"]["page"]}/{result["pagination"]["pages"]}, '
            f'{result["pagination"]["total"]} total items)'
        )
        
    except PermissionError:
        current_app.logger.error(
            f'[browse] 403 Forbidden – Permission denied trying to access: {full_path} (user: {current_user.id})'
        )
        abort(403)
    except Exception as e:
        current_app.logger.error(f'[browse] Error listing directory {full_path}: {e}')
        abort(500)

    # If the requested page is out of range, redirect to the last valid page
    if page > result['pagination']['pages'] and result['pagination']['pages'] > 0:
        return redirect(url_for('browser.browse', 
                               mount_id=mount_id, 
                               subpath=subpath,
                               page=result['pagination']['pages'],
                               per_page=per_page,
                               sort=sort_by,
                               **({'desc': ''} if sort_desc else {})))

    return render_template('browse.html', 
                         contents=result['items'],
                         pagination=result['pagination'],
                         path=subpath,             # Just the path within the mount directory
                         mount_id=mount_id,        # The actual mount directory name
                         current_sort=sort_by,
                         sort_desc=sort_desc,
                         per_page=per_page)

# API endpoint for AJAX requests
@browser_bp.route('/api/browse/<mount_id>', defaults={'subpath': ''})
@browser_bp.route('/api/browse/<mount_id>/<path:subpath>')
@login_required
def api_browse(mount_id, subpath):
    """
    JSON API endpoint for paginated directory browsing.
    
    Returns the same data as the browse route but as JSON for AJAX requests.
    This allows the frontend to dynamically load pages without full page refreshes.
    """
    
    base_path = get_mount_base()
    full_subpath = os.path.join(mount_id, subpath) if subpath else mount_id
    full_path = safe_join(base_path, full_subpath)

    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        return jsonify({'error': 'Directory not found'}), 404

    # Get pagination parameters
    try:
        page = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
        
    try:
        per_page = min(500, max(10, int(request.args.get('per_page', 100))))
    except (ValueError, TypeError):
        per_page = 100
        
    sort_by = request.args.get('sort', 'name')
    if sort_by not in ['name', 'size', 'modified', 'type']:
        sort_by = 'name'
        
    sort_desc = 'desc' in request.args

    try:
        result = list_directory_paginated(
            directory=full_path,
            mount_id=mount_id,
            base_subpath=subpath,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        
        return jsonify(result)
        
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        current_app.logger.error(f'[api_browse] Error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@browser_bp.route('/view/<mount_id>/<path:subpath>')
@login_required
def view_file(mount_id, subpath):
    """
    Display file contents in the browser with syntax highlighting.
    
    This route renders file contents for viewing in the browser interface.
    It includes syntax highlighting for supported file types and handles
    binary files by offering download instead of display.
        
    Note:
        Files that are not in SAFE_MIME_TYPES are automatically downloaded
        instead of displayed to prevent security issues with executable content.
    """

    base_path = get_mount_base()

    # Combine mount_id and subpath for the full path
    full_subpath = os.path.join(mount_id, subpath)
    full_path = safe_join(base_path, full_subpath)
    file_ext = os.path.splitext(full_path)[1].lower()

    # Verify file exists and is actually a file
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        current_app.logger.error(
            '[view] 404 Not Found – File not found: %s', full_path
        )
        abort(404)

    # Check if file type is safe for viewing
    mime_type, _ = mimetypes.guess_type(full_path)
    if mime_type not in SAFE_MIME_TYPES:
        current_app.logger.info(f'[view] File {full_path} is not a valid mime type for viewing')
        current_app.logger.info(f'[view] MIME: {mime_type} | Extension: {file_ext}')
        # For unsafe MIME types, force download instead of display
        return send_file(full_path)

    try:
        # Read file content with UTF-8 encoding and error handling
        with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        current_app.logger.error(
            '[view] 500 Error – Unable to open file: %s', full_path
        )
        abort(500)

    # Determine syntax highlighting language
    _, ext = os.path.splitext(full_path)
    prism_lang = EXTENSION_TO_PRISM.get(ext.lower(), 'none')

    # Log successful file access
    current_app.logger.info(
        f'[view] User {current_user.id} viewed file: {full_path}'
    )

    return render_template(
        'view_file.html',
        content=html.escape(content), # Prevents XSS attacks but leaves the HTML entities like: &#x27; for single quotes
        lang=prism_lang,
        file_path=subpath,
        file_size=os.path.getsize(full_path),
        mime_type=mime_type,
        mount_id=mount_id
    )

@browser_bp.route('/download/<mount_id>/<path:subpath>')
@login_required
def download_file(mount_id, subpath):
    """
    Download a file from the mount point.
    
    This route serves files for download with proper headers to trigger
    browser download behavior. It handles both text and binary files safely.
    """

    base_path = get_mount_base()

    # Combine mount_id and subpath for the full path
    full_subpath = os.path.join(mount_id, subpath)
    full_path = safe_join(base_path, full_subpath)

    # Verify file exists and is actually a file
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        current_app.logger.error(
            '[download] 404 Not Found – File not found: %s', full_path
        )
        abort(404)

    # Log download activity for security auditing
    current_app.logger.info(
        f'[download] User {current_user.id} downloaded file: {full_path}'
    )

    # Serve file with attachment headers to force download
    return send_file(full_path, as_attachment=True)

@browser_bp.route('/metadata/<mount_id>/<path:subpath>')
@login_required
def file_metadata(mount_id, subpath):
    """
    Retrieve metadata information for a file or directory.
    
    This route returns detailed metadata about a file or directory as JSON.
    It's used by the frontend for displaying file information and can be
    called via AJAX requests.
    """

    base_path = get_mount_base()
    # Combine mount_id and subpath for the full path
    full_subpath = os.path.join(mount_id, subpath)
    full_path = safe_join(base_path, full_subpath)

    # Verify path exists
    if not os.path.exists(full_path):
        current_app.logger.error(
            '[metadata] 404 Not Found – File metadata not found: %s', full_path
        )
        abort(404)

    # Get file statistics
    stat = os.stat(full_path)

    # Log metadata access
    current_app.logger.debug(
        f'[metadata] User {current_user.id} requested metadata for: {full_path}'
    )

    # Return metadata as JSON
    return jsonify({
        'name': os.path.basename(full_path),
        'size': stat.st_size,
        'modified': stat.st_mtime,
        'is_dir': os.path.isdir(full_path),
        'permissions': oct(stat.st_mode)[-3:]
    })
