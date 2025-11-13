<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Chat management
 *
 * @package    local_aiassistant
 * @copyright  2024 AI Assistant Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_aiassistant;

defined('MOODLE_INTERNAL') || die();

/**
 * Class for managing chats and messages
 */
class chat_manager {
    /**
     * Create a new chat session
     *
     * @param int $userid User ID
     * @param string $theme Theme name
     * @param string $title Optional title
     * @return int Chat ID
     */
    public static function create_chat($userid, $theme = 'default', $title = '') {
        global $DB;

        $chat = new \stdClass();
        $chat->userid = $userid;
        $chat->theme = $theme;
        $chat->title = $title;
        $chat->timecreated = time();
        $chat->timemodified = time();

        return $DB->insert_record('local_aiassistant_chats', $chat);
    }

    /**
     * Add a message to a chat
     *
     * @param int $chatid Chat ID
     * @param string $role Role (user or assistant)
     * @param string $content Message content
     * @param array $metadata Optional metadata
     * @return int Message ID
     */
    public static function add_message($chatid, $role, $content, $metadata = []) {
        global $DB;

        $message = new \stdClass();
        $message->chatid = $chatid;
        $message->role = $role;
        $message->content = $content;
        $message->metadata = json_encode($metadata);
        $message->timecreated = time();

        $messageid = $DB->insert_record('local_aiassistant_messages', $message);

        // Update chat timemodified
        $DB->set_field('local_aiassistant_chats', 'timemodified', time(), ['id' => $chatid]);

        // Auto-generate title from first user message if not set
        if ($role === 'user') {
            $chat = $DB->get_record('local_aiassistant_chats', ['id' => $chatid]);
            if (empty($chat->title)) {
                $title = self::generate_title($content);
                $DB->set_field('local_aiassistant_chats', 'title', $title, ['id' => $chatid]);
            }
        }

        return $messageid;
    }

    /**
     * Get all messages for a chat
     *
     * @param int $chatid Chat ID
     * @return array Messages
     */
    public static function get_messages($chatid) {
        global $DB;

        $messages = $DB->get_records('local_aiassistant_messages',
            ['chatid' => $chatid],
            'timecreated ASC'
        );

        foreach ($messages as $message) {
            $message->metadata = json_decode($message->metadata, true);
        }

        return array_values($messages);
    }

    /**
     * Get chat history for a user
     *
     * @param int $userid User ID
     * @param int $limit Limit
     * @return array Chats
     */
    public static function get_user_chats($userid, $limit = 50) {
        global $DB;

        return $DB->get_records('local_aiassistant_chats',
            ['userid' => $userid],
            'timemodified DESC',
            '*',
            0,
            $limit
        );
    }

    /**
     * Get a chat by ID
     *
     * @param int $chatid Chat ID
     * @return object|false Chat record
     */
    public static function get_chat($chatid) {
        global $DB;
        return $DB->get_record('local_aiassistant_chats', ['id' => $chatid]);
    }

    /**
     * Delete a chat and its messages
     *
     * @param int $chatid Chat ID
     * @return bool Success
     */
    public static function delete_chat($chatid) {
        global $DB;

        $DB->delete_records('local_aiassistant_messages', ['chatid' => $chatid]);
        return $DB->delete_records('local_aiassistant_chats', ['id' => $chatid]);
    }

    /**
     * Generate a title from message content
     *
     * @param string $content Message content
     * @return string Title
     */
    private static function generate_title($content) {
        $title = strip_tags($content);
        $title = substr($title, 0, 50);
        if (strlen($content) > 50) {
            $title .= '...';
        }
        return $title;
    }

    /**
     * Update chat title
     *
     * @param int $chatid Chat ID
     * @param string $title New title
     * @return bool Success
     */
    public static function update_title($chatid, $title) {
        global $DB;
        return $DB->set_field('local_aiassistant_chats', 'title', $title, ['id' => $chatid]);
    }
}
