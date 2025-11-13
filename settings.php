<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Settings for local_aiassistant
 *
 * @package    local_aiassistant
 * @copyright  2024 Ashish Sengar
 * @author     Ashish Sengar <sengarashish@users.noreply.github.com>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {
    $settings = new admin_settingpage('local_aiassistant', get_string('settings', 'local_aiassistant'));

    // LLM Provider
    $settings->add(new admin_setting_configselect(
        'local_aiassistant/llmprovider',
        get_string('llmprovider', 'local_aiassistant'),
        get_string('llmprovider_desc', 'local_aiassistant'),
        'openai',
        [
            'openai' => get_string('openai', 'local_aiassistant'),
            'anthropic' => get_string('anthropic', 'local_aiassistant'),
        ]
    ));

    // OpenAI API Key
    $settings->add(new admin_setting_configpasswordunmask(
        'local_aiassistant/openaiapikey',
        get_string('openaiapikey', 'local_aiassistant'),
        get_string('openaiapikey_desc', 'local_aiassistant'),
        ''
    ));

    // Anthropic API Key
    $settings->add(new admin_setting_configpasswordunmask(
        'local_aiassistant/anthropicapikey',
        get_string('anthropicapikey', 'local_aiassistant'),
        get_string('anthropicapikey_desc', 'local_aiassistant'),
        ''
    ));

    // Backend URL
    $settings->add(new admin_setting_configtext(
        'local_aiassistant/backendurl',
        get_string('backendurl', 'local_aiassistant'),
        get_string('backendurl_desc', 'local_aiassistant'),
        'http://localhost:8000',
        PARAM_URL
    ));

    // Default Theme
    $settings->add(new admin_setting_configselect(
        'local_aiassistant/defaulttheme',
        get_string('defaulttheme', 'local_aiassistant'),
        get_string('defaulttheme_desc', 'local_aiassistant'),
        'default',
        [
            'default' => get_string('theme_default', 'local_aiassistant'),
            'jungle' => get_string('theme_jungle', 'local_aiassistant'),
            'ocean' => get_string('theme_ocean', 'local_aiassistant'),
            'space' => get_string('theme_space', 'local_aiassistant'),
        ]
    ));

    // Enable Age-Based Responses
    $settings->add(new admin_setting_configcheckbox(
        'local_aiassistant/enableageresponses',
        get_string('enableageresponses', 'local_aiassistant'),
        get_string('enableageresponses_desc', 'local_aiassistant'),
        1
    ));

    // Serper API Key for internet search
    $settings->add(new admin_setting_configpasswordunmask(
        'local_aiassistant/serperapikey',
        get_string('serperapikey', 'local_aiassistant'),
        get_string('serperapikey_desc', 'local_aiassistant'),
        ''
    ));

    $ADMIN->add('localplugins', $settings);

    // Add knowledge base management page
    $ADMIN->add('localplugins', new admin_externalpage(
        'local_aiassistant_documents',
        get_string('knowledgebase', 'local_aiassistant'),
        new moodle_url('/local/aiassistant/manage_documents.php'),
        'local/aiassistant:managecontent'
    ));
}
