<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * API client for backend communication
 *
 * @package    local_aiassistant
 * @copyright  2024 AI Assistant Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_aiassistant;

defined('MOODLE_INTERNAL') || die();

/**
 * Client for communicating with Python backend
 */
class api_client {
    /**
     * Send chat request to backend
     *
     * @param string $backendurl Backend URL
     * @param string $message User message
     * @param array $history Chat history
     * @param int|null $userage User age
     * @return array Response
     */
    public static function chat($backendurl, $message, $history, $userage = null) {
        $url = rtrim($backendurl, '/') . '/api/chat';

        $data = [
            'message' => $message,
            'history' => self::format_history($history),
            'user_age' => $userage,
            'llm_provider' => get_config('local_aiassistant', 'llmprovider'),
            'api_key' => self::get_api_key(),
        ];

        return self::send_request($url, $data);
    }

    /**
     * Send document for ingestion
     *
     * @param string $backendurl Backend URL
     * @param int $documentid Document ID
     * @param string $source File path or URL
     * @param string $type Document type
     * @return array Response
     */
    public static function ingest_document($backendurl, $documentid, $source, $type) {
        $url = rtrim($backendurl, '/') . '/api/ingest/' . $type;

        $data = [
            'document_id' => $documentid,
            'source' => $source,
        ];

        // For PDF files, we need to send the file content
        if ($type === 'pdf' && file_exists($source)) {
            $data['file_content'] = base64_encode(file_get_contents($source));
            $data['filename'] = basename($source);
        }

        return self::send_request($url, $data);
    }

    /**
     * Send HTTP request
     *
     * @param string $url URL
     * @param array $data Request data
     * @return array Response
     */
    private static function send_request($url, $data) {
        $curl = curl_init();

        curl_setopt_array($curl, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($data),
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
            ],
            CURLOPT_TIMEOUT => 60,
        ]);

        $response = curl_exec($curl);
        $httpcode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        $error = curl_error($curl);

        curl_close($curl);

        if ($error) {
            throw new \Exception('Backend connection error: ' . $error);
        }

        if ($httpcode !== 200) {
            throw new \Exception('Backend error: HTTP ' . $httpcode);
        }

        $result = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new \Exception('Invalid JSON response from backend');
        }

        return $result;
    }

    /**
     * Format chat history for backend
     *
     * @param array $messages Messages
     * @return array Formatted history
     */
    private static function format_history($messages) {
        $history = [];
        foreach ($messages as $msg) {
            $history[] = [
                'role' => $msg->role,
                'content' => $msg->content,
            ];
        }
        return $history;
    }

    /**
     * Get API key for current provider
     *
     * @return string API key
     */
    private static function get_api_key() {
        $provider = get_config('local_aiassistant', 'llmprovider');
        $configkey = $provider . 'apikey';
        return get_config('local_aiassistant', $configkey);
    }
}
