"""
Utility functions for EFS Navigator file system operations with pagination support.

This module provides secure file system operations, path resolution, and paginated directory
listing functionality with built-in security controls to prevent path traversal
attacks and ensure safe file access within designated mount points.
"""

import os
from pathlib import Path
from flask import current_app
from typing import Dict, List, Tuple, Optional

def get_mount_base():
    """
    Determine the correct base path for file browsing based on application mode.
    
    Returns the appropriate mount base directory depending on whether the
    application is running in development or production mode. This allows
    for different file system configurations between environments.
    """

    mode = current_app.config['MODE']
    current_app.logger.debug(f'→ get_mount_base() sees MODE={mode}')

    return current_app.config['MOUNT_BASE']

def list_directory_paginated(directory, mount_id=None, base_subpath='', page=1, per_page=100, sort_by='name', sort_desc=False):
    """
    Generate a paginated list of file and folder metadata for the specified directory.
    
    Scans the specified directory and returns detailed information about files
    and subdirectories with pagination support to handle large directories efficiently.
    """
    
    # Get all entries first
    try:
        entries = []
        with os.scandir(directory) as scanner:
            for entry in scanner:
                try:
                    stat_info = entry.stat()
                    full_path = os.path.join(directory, entry.name)
                    rel_path = os.path.join(base_subpath, entry.name)

                    item = {
                        'name': entry.name,
                        'is_dir': entry.is_dir(),
                        'size': stat_info.st_size if not entry.is_dir() else 0,
                        'permissions': oct(stat_info.st_mode)[-3:],
                        'path': rel_path.replace('\\', '/'),
                        'modified': int(stat_info.st_mtime)
                    }
                    entries.append(item)
                except (OSError, IOError) as e:
                    # Skip files we can't stat (permissions, etc.)
                    current_app.logger.warning(f"Could not stat {entry.name}: {e}")
                    continue
    except PermissionError:
        raise
    except Exception as e:
        current_app.logger.error(f"Error scanning directory {directory}: {e}")
        raise

    # Sort entries
    sort_key_map = {
        'name': lambda x: x['name'].lower(),
        'size': lambda x: x['size'],
        'modified': lambda x: x['modified'],
        'type': lambda x: (not x['is_dir'], x['name'].lower())  # Directories first, then by name
    }
    
    if sort_by in sort_key_map:
        entries.sort(key=sort_key_map[sort_by], reverse=sort_desc)
    else:
        # Default sort by name
        entries.sort(key=lambda x: x['name'].lower(), reverse=sort_desc)

    # Calculate pagination
    total_items = len(entries)
    total_pages = (total_items + per_page - 1) // per_page  # Ceiling division
    
    # Validate page number
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate slice indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Get page items
    page_items = entries[start_idx:end_idx]
    
    # Pagination metadata
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_items,
        'pages': total_pages,
        'has_prev': page > 1,
        'prev_num': page - 1 if page > 1 else None,
        'has_next': page < total_pages,
        'next_num': page + 1 if page < total_pages else None,
        'start_item': start_idx + 1 if total_items > 0 else 0,
        'end_item': min(end_idx, total_items)
    }
    
    return {
        'items': page_items,
        'pagination': pagination
    }

def list_directory(directory, mount_id=None, base_subpath=''):
    """
    Legacy function for backward compatibility.
    
    This maintains the original interface but now uses pagination internally
    with a large default page size to avoid breaking existing code.
    """
    
    result = list_directory_paginated(
        directory=directory,
        mount_id=mount_id,
        base_subpath=base_subpath,
        page=1,
        per_page=10000
    )
    
    return result['items']

def safe_join(base, *paths):
    """
    Securely join path components while preventing path traversal attacks.

    Joins one or more path elements to a base path and ensures the resulting
    path remains within the base directory. This prevents malicious attempts
    to access files outside the intended directory structure.
    """

    final_path = os.path.abspath(os.path.join(base, *paths))

    if not final_path.startswith(os.path.abspath(base)):
        raise ValueError('Attempted to access outside base directory')

    return final_path

def resolve_path(subpath: str) -> Path:
    """
    Safely resolve a subpath under the correct base directory.
    
    Takes a relative subpath and resolves it against the current application's
    mount base directory while ensuring the resolved path stays within bounds.
    """

    base = Path(get_mount_base()).resolve()
    target_path = (base / subpath).resolve()

    if not str(target_path).startswith(str(base)):
        raise ValueError('Invalid path traversal detected.')

    return target_path

def safe_listdir(directory: Path) -> list[str]:
    """
    Return a sorted list of file and folder names in the given directory.
    
    Provides a safe wrapper around directory listing with proper error handling
    and validation to ensure the target is actually a directory.
    """

    if not directory.is_dir():
        raise NotADirectoryError(f'{directory} is not a valid directory.')

    return sorted(entry.name for entry in directory.iterdir())
