"""
Main application routes for EFS Navigator dashboard.

This module defines the core application routes that are not part of specific
blueprints, including the main dashboard that displays available mount points
and serves as the application's primary entry point.
"""

import os
from flask import render_template, current_app
from flask_login import login_required
from app.browser.utils import get_mount_base

def register_routes(app):
    """
    Registers general, non-namespaced routes to the Flask app.
    This should only include simple routes like index, health checks, etc.
    """

    @app.route("/", endpoint="dashboard")
    @app.route("/index", endpoint="index")
    @login_required
    def dashboard():
        """
        Display the main dashboard with available mount points.
        """

        mount_base = get_mount_base()
        try:
            entries = sorted(os.listdir(mount_base))
            mounts = [entry for entry in entries
                     if os.path.isdir(os.path.join(mount_base, entry))]
            current_app.logger.info(
                "[dashboard] Found %d mount points at %s",
                len(mounts), mount_base)

        except (OSError, IOError, PermissionError) as error:
            current_app.logger.error(
                "[dashboard] Failed to list mount points: %s", error)
            mounts = []

        return render_template("index.html", mounts=mounts)
