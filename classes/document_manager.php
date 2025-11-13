<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Document management for knowledge base
 *
 * @package    local_aiassistant
 * @copyright  2024 AI Assistant Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_aiassistant;

defined('MOODLE_INTERNAL') || die();

/**
 * Class for managing documents in the knowledge base
 */
class document_manager {
    /**
     * Add a document record
     *
     * @param string $title Document title
     * @param string $sourcetype Source type (pdf, url)
     * @param int $uploaderid Uploader user ID
     * @param string $sourceurl Optional source URL
     * @param string $filepath Optional file path
     * @return int Document ID
     */
    public static function add_document($title, $sourcetype, $uploaderid, $sourceurl = '', $filepath = '') {
        global $DB;

        $document = new \stdClass();
        $document->title = $title;
        $document->sourcetype = $sourcetype;
        $document->sourceurl = $sourceurl;
        $document->filepath = $filepath;
        $document->status = 'pending';
        $document->chunks = 0;
        $document->uploaderid = $uploaderid;
        $document->timecreated = time();
        $document->timemodified = time();

        return $DB->insert_record('local_aiassistant_documents', $document);
    }

    /**
     * Update document status
     *
     * @param int $documentid Document ID
     * @param string $status New status
     * @param int $chunks Number of chunks
     * @return bool Success
     */
    public static function update_status($documentid, $status, $chunks = 0) {
        global $DB;

        $document = new \stdClass();
        $document->id = $documentid;
        $document->status = $status;
        $document->chunks = $chunks;
        $document->timemodified = time();

        return $DB->update_record('local_aiassistant_documents', $document);
    }

    /**
     * Get all documents
     *
     * @return array Documents
     */
    public static function get_all_documents() {
        global $DB;
        return $DB->get_records('local_aiassistant_documents', null, 'timecreated DESC');
    }

    /**
     * Get a document by ID
     *
     * @param int $documentid Document ID
     * @return object|false Document record
     */
    public static function get_document($documentid) {
        global $DB;
        return $DB->get_record('local_aiassistant_documents', ['id' => $documentid]);
    }

    /**
     * Delete a document
     *
     * @param int $documentid Document ID
     * @return bool Success
     */
    public static function delete_document($documentid) {
        global $DB;

        $document = self::get_document($documentid);
        if (!$document) {
            return false;
        }

        // Delete file if exists
        if (!empty($document->filepath)) {
            @unlink($document->filepath);
        }

        return $DB->delete_records('local_aiassistant_documents', ['id' => $documentid]);
    }

    /**
     * Get document statistics
     *
     * @return object Statistics
     */
    public static function get_statistics() {
        global $DB;

        $stats = new \stdClass();
        $stats->total = $DB->count_records('local_aiassistant_documents');
        $stats->pending = $DB->count_records('local_aiassistant_documents', ['status' => 'pending']);
        $stats->processing = $DB->count_records('local_aiassistant_documents', ['status' => 'processing']);
        $stats->completed = $DB->count_records('local_aiassistant_documents', ['status' => 'completed']);
        $stats->failed = $DB->count_records('local_aiassistant_documents', ['status' => 'failed']);

        return $stats;
    }
}
