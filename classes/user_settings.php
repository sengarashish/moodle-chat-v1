<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * User settings management
 *
 * @package    local_aiassistant
 * @copyright  2024 AI Assistant Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_aiassistant;

defined('MOODLE_INTERNAL') || die();

/**
 * Class for managing user-specific settings
 */
class user_settings {
    /**
     * Get a user setting
     *
     * @param int $userid User ID
     * @param string $name Setting name
     * @param mixed $default Default value
     * @return mixed Setting value
     */
    public static function get_setting($userid, $name, $default = null) {
        global $DB;

        $record = $DB->get_record('local_aiassistant_settings', [
            'userid' => $userid,
            'name' => $name,
        ]);

        return $record ? $record->value : $default;
    }

    /**
     * Set a user setting
     *
     * @param int $userid User ID
     * @param string $name Setting name
     * @param mixed $value Setting value
     * @return bool Success
     */
    public static function set_setting($userid, $name, $value) {
        global $DB;

        $record = $DB->get_record('local_aiassistant_settings', [
            'userid' => $userid,
            'name' => $name,
        ]);

        if ($record) {
            $record->value = $value;
            $record->timemodified = time();
            return $DB->update_record('local_aiassistant_settings', $record);
        } else {
            $record = new \stdClass();
            $record->userid = $userid;
            $record->name = $name;
            $record->value = $value;
            $record->timemodified = time();
            return $DB->insert_record('local_aiassistant_settings', $record);
        }
    }

    /**
     * Get all settings for a user
     *
     * @param int $userid User ID
     * @return array Settings array
     */
    public static function get_all_settings($userid) {
        global $DB;

        $records = $DB->get_records('local_aiassistant_settings', ['userid' => $userid]);
        $settings = [];

        foreach ($records as $record) {
            $settings[$record->name] = $record->value;
        }

        return $settings;
    }
}
