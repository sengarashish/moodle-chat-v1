<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * REST API endpoints for AI Assistant
 *
 * @package    local_aiassistant
 * @copyright  2024 AI Assistant Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

define('AJAX_SCRIPT', true);

require_once(__DIR__ . '/../../config.php');

require_login();
require_sesskey();

$action = required_param('action', PARAM_ALPHA);

header('Content-Type: application/json');

try {
    switch ($action) {
        case 'chat':
            require_capability('local/aiassistant:use', context_system::instance());
            $message = required_param('message', PARAM_RAW);
            $chatid = optional_param('chatid', 0, PARAM_INT);
            $theme = optional_param('theme', 'default', PARAM_ALPHA);

            // Create new chat if needed
            if (empty($chatid)) {
                $chatid = \local_aiassistant\chat_manager::create_chat($USER->id, $theme);
            }

            // Save user message
            \local_aiassistant\chat_manager::add_message($chatid, 'user', $message);

            // Get chat history for context
            $messages = \local_aiassistant\chat_manager::get_messages($chatid);

            // Get user age for age-based responses
            $userage = null;
            if (get_config('local_aiassistant', 'enableageresponses') && !empty($USER->profile['age'])) {
                $userage = $USER->profile['age'];
            }

            // Call backend API
            $backendurl = get_config('local_aiassistant', 'backendurl');
            $response = \local_aiassistant\api_client::chat($backendurl, $message, $messages, $userage);

            // Save assistant response
            \local_aiassistant\chat_manager::add_message($chatid, 'assistant', $response['content'], [
                'sources' => $response['sources'] ?? [],
                'model' => $response['model'] ?? '',
            ]);

            echo json_encode([
                'success' => true,
                'chatid' => $chatid,
                'response' => $response,
            ]);
            break;

        case 'get_history':
            require_capability('local/aiassistant:use', context_system::instance());
            $chats = \local_aiassistant\chat_manager::get_user_chats($USER->id);

            echo json_encode([
                'success' => true,
                'chats' => array_values($chats),
            ]);
            break;

        case 'get_messages':
            require_capability('local/aiassistant:use', context_system::instance());
            $chatid = required_param('chatid', PARAM_INT);

            $chat = \local_aiassistant\chat_manager::get_chat($chatid);
            if (!$chat || $chat->userid != $USER->id) {
                throw new moodle_exception('nopermission');
            }

            $messages = \local_aiassistant\chat_manager::get_messages($chatid);

            echo json_encode([
                'success' => true,
                'messages' => $messages,
                'chat' => $chat,
            ]);
            break;

        case 'delete_chat':
            require_capability('local/aiassistant:use', context_system::instance());
            $chatid = required_param('chatid', PARAM_INT);

            $chat = \local_aiassistant\chat_manager::get_chat($chatid);
            if (!$chat || $chat->userid != $USER->id) {
                throw new moodle_exception('nopermission');
            }

            \local_aiassistant\chat_manager::delete_chat($chatid);

            echo json_encode([
                'success' => true,
            ]);
            break;

        case 'upload_document':
            require_capability('local/aiassistant:managecontent', context_system::instance());
            $title = required_param('title', PARAM_TEXT);

            // Handle file upload
            if (isset($_FILES['file']) && $_FILES['file']['error'] === UPLOAD_ERR_OK) {
                $uploaddir = $CFG->dataroot . '/aiassistant/uploads/';
                if (!is_dir($uploaddir)) {
                    mkdir($uploaddir, 0755, true);
                }

                $filename = uniqid() . '_' . basename($_FILES['file']['name']);
                $filepath = $uploaddir . $filename;

                if (move_uploaded_file($_FILES['file']['tmp_name'], $filepath)) {
                    $documentid = \local_aiassistant\document_manager::add_document(
                        $title,
                        'pdf',
                        $USER->id,
                        '',
                        $filepath
                    );

                    // Send to backend for processing
                    $backendurl = get_config('local_aiassistant', 'backendurl');
                    \local_aiassistant\api_client::ingest_document($backendurl, $documentid, $filepath, 'pdf');

                    echo json_encode([
                        'success' => true,
                        'documentid' => $documentid,
                    ]);
                } else {
                    throw new Exception('File upload failed');
                }
            } else {
                throw new Exception('No file uploaded');
            }
            break;

        case 'add_url':
            require_capability('local/aiassistant:managecontent', context_system::instance());
            $title = required_param('title', PARAM_TEXT);
            $url = required_param('url', PARAM_URL);

            $documentid = \local_aiassistant\document_manager::add_document(
                $title,
                'url',
                $USER->id,
                $url
            );

            // Send to backend for processing
            $backendurl = get_config('local_aiassistant', 'backendurl');
            \local_aiassistant\api_client::ingest_document($backendurl, $documentid, $url, 'url');

            echo json_encode([
                'success' => true,
                'documentid' => $documentid,
            ]);
            break;

        default:
            throw new moodle_exception('invalidaction');
    }
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage(),
    ]);
}
