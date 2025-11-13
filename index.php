<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * AI Assistant main page
 *
 * @package    local_aiassistant
 * @copyright  2024 AI Assistant Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once(__DIR__ . '/../../config.php');
require_once($CFG->libdir . '/adminlib.php');

require_login();
require_capability('local/aiassistant:use', context_system::instance());

$chatid = optional_param('chatid', 0, PARAM_INT);
$theme = optional_param('theme', '', PARAM_ALPHA);

$PAGE->set_url(new moodle_url('/local/aiassistant/index.php'));
$PAGE->set_context(context_system::instance());
$PAGE->set_title(get_string('aiassistant', 'local_aiassistant'));
$PAGE->set_heading(get_string('aiassistant', 'local_aiassistant'));
$PAGE->set_pagelayout('standard');

// Get user's selected theme or default
if (empty($theme)) {
    $theme = \local_aiassistant\user_settings::get_setting($USER->id, 'theme',
        get_config('local_aiassistant', 'defaulttheme'));
}

// Load JavaScript module
$PAGE->requires->js_call_amd('local_aiassistant/chat', 'init', [
    'userid' => $USER->id,
    'chatid' => $chatid,
    'theme' => $theme,
    'backendurl' => get_config('local_aiassistant', 'backendurl'),
    'sesskey' => sesskey(),
]);

echo $OUTPUT->header();

// Theme selector and new chat button
echo html_writer::start_div('aiassistant-controls');
echo html_writer::start_div('aiassistant-theme-selector');
echo html_writer::label(get_string('theme', 'local_aiassistant'), 'theme-select');
echo html_writer::select(
    [
        'default' => get_string('theme_default', 'local_aiassistant'),
        'jungle' => get_string('theme_jungle', 'local_aiassistant'),
        'ocean' => get_string('theme_ocean', 'local_aiassistant'),
        'space' => get_string('theme_space', 'local_aiassistant'),
    ],
    'theme',
    $theme,
    false,
    ['id' => 'theme-select', 'class' => 'custom-select']
);
echo html_writer::end_div();
echo html_writer::tag('button', get_string('newchat', 'local_aiassistant'), [
    'id' => 'new-chat-btn',
    'class' => 'btn btn-primary',
]);
echo html_writer::end_div();

// Main chat container
echo html_writer::start_div('aiassistant-container theme-' . $theme);

// Chat history sidebar
echo html_writer::start_div('aiassistant-sidebar');
echo html_writer::tag('h3', get_string('chathistory', 'local_aiassistant'));
echo html_writer::div('', 'chat-history-list', ['id' => 'chat-history']);
echo html_writer::end_div();

// Chat area
echo html_writer::start_div('aiassistant-chat-area');
echo html_writer::div('', 'chat-messages', ['id' => 'chat-messages']);

// Input area
echo html_writer::start_div('chat-input-area');
echo html_writer::tag('textarea', '', [
    'id' => 'chat-input',
    'placeholder' => get_string('typeamessage', 'local_aiassistant'),
    'rows' => 3,
]);
echo html_writer::tag('button', get_string('sendmessage', 'local_aiassistant'), [
    'id' => 'send-btn',
    'class' => 'btn btn-primary',
]);
echo html_writer::end_div();
echo html_writer::end_div();

echo html_writer::end_div(); // End container

echo $OUTPUT->footer();
