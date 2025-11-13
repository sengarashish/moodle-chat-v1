// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Document management JavaScript
 *
 * @module     local_aiassistant/documents
 * @copyright  2024 AI Assistant Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

define(['jquery', 'core/notification'], function($, Notification) {

    var backendUrl = '';
    var sesskey = '';

    /**
     * Initialize document management
     */
    var init = function(config) {
        backendUrl = config.backendurl;
        sesskey = config.sesskey;

        // PDF upload form
        $('#upload-pdf-form').on('submit', function(e) {
            e.preventDefault();
            uploadPDF();
        });

        // URL form
        $('#add-url-form').on('submit', function(e) {
            e.preventDefault();
            addURL();
        });
    };

    /**
     * Upload PDF document
     */
    var uploadPDF = function() {
        var formData = new FormData();
        formData.append('action', 'upload_document');
        formData.append('sesskey', M.cfg.sesskey);
        formData.append('title', $('#pdf-title').val());
        formData.append('file', $('#pdf-file')[0].files[0]);

        // Disable form
        $('#upload-pdf-form button').prop('disabled', true);

        $.ajax({
            url: M.cfg.wwwroot + '/local/aiassistant/api.php',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    Notification.alert('Success', 'Document uploaded successfully', 'OK');
                    $('#upload-pdf-form')[0].reset();
                    location.reload(); // Reload to show new document
                } else {
                    Notification.alert('Error', response.error || 'Upload failed', 'OK');
                }
            },
            error: function() {
                Notification.alert('Error', 'Could not upload document', 'OK');
            },
            complete: function() {
                $('#upload-pdf-form button').prop('disabled', false);
            }
        });
    };

    /**
     * Add URL
     */
    var addURL = function() {
        var title = $('#url-title').val();
        var url = $('#url-input').val();

        // Disable form
        $('#add-url-form button').prop('disabled', true);

        $.ajax({
            url: M.cfg.wwwroot + '/local/aiassistant/api.php',
            method: 'POST',
            data: {
                action: 'add_url',
                sesskey: M.cfg.sesskey,
                title: title,
                url: url
            },
            success: function(response) {
                if (response.success) {
                    Notification.alert('Success', 'URL added successfully', 'OK');
                    $('#add-url-form')[0].reset();
                    location.reload(); // Reload to show new document
                } else {
                    Notification.alert('Error', response.error || 'Failed to add URL', 'OK');
                }
            },
            error: function() {
                Notification.alert('Error', 'Could not add URL', 'OK');
            },
            complete: function() {
                $('#add-url-form button').prop('disabled', false);
            }
        });
    };

    return {
        init: init
    };
});
