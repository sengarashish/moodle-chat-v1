<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Knowledge base document management
 *
 * @package    local_aiassistant
 * @copyright  2024 AI Assistant Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once(__DIR__ . '/../../config.php');
require_once($CFG->libdir . '/adminlib.php');

admin_externalpage_setup('local_aiassistant_documents');
require_capability('local/aiassistant:managecontent', context_system::instance());

$action = optional_param('action', '', PARAM_ALPHA);
$documentid = optional_param('id', 0, PARAM_INT);

$PAGE->set_url(new moodle_url('/local/aiassistant/manage_documents.php'));
$PAGE->set_title(get_string('knowledgebase', 'local_aiassistant'));
$PAGE->set_heading(get_string('knowledgebase', 'local_aiassistant'));

// Handle actions
if ($action === 'delete' && $documentid && confirm_sesskey()) {
    \local_aiassistant\document_manager::delete_document($documentid);
    redirect($PAGE->url, get_string('documentdeleted', 'local_aiassistant'));
}

// Load JavaScript
$PAGE->requires->js_call_amd('local_aiassistant/documents', 'init', [
    'backendurl' => get_config('local_aiassistant', 'backendurl'),
    'sesskey' => sesskey(),
]);

echo $OUTPUT->header();

// Upload form
echo html_writer::start_div('document-upload-forms');

// PDF upload
echo html_writer::start_div('upload-form');
echo html_writer::tag('h3', get_string('uploaddocument', 'local_aiassistant'));
echo html_writer::start_tag('form', [
    'id' => 'upload-pdf-form',
    'enctype' => 'multipart/form-data',
]);
echo html_writer::label(get_string('documenttitle', 'local_aiassistant'), 'pdf-title');
echo html_writer::empty_tag('input', [
    'type' => 'text',
    'id' => 'pdf-title',
    'name' => 'title',
    'required' => 'required',
    'class' => 'form-control',
]);
echo html_writer::label(get_string('documentfile', 'local_aiassistant'), 'pdf-file');
echo html_writer::empty_tag('input', [
    'type' => 'file',
    'id' => 'pdf-file',
    'name' => 'file',
    'accept' => '.pdf',
    'required' => 'required',
    'class' => 'form-control',
]);
echo html_writer::tag('button', get_string('upload', 'local_aiassistant'), [
    'type' => 'submit',
    'class' => 'btn btn-primary',
]);
echo html_writer::end_tag('form');
echo html_writer::end_div();

// URL form
echo html_writer::start_div('upload-form');
echo html_writer::tag('h3', get_string('addurl', 'local_aiassistant'));
echo html_writer::start_tag('form', ['id' => 'add-url-form']);
echo html_writer::label(get_string('documenttitle', 'local_aiassistant'), 'url-title');
echo html_writer::empty_tag('input', [
    'type' => 'text',
    'id' => 'url-title',
    'name' => 'title',
    'required' => 'required',
    'class' => 'form-control',
]);
echo html_writer::label(get_string('documenturl', 'local_aiassistant'), 'url-input');
echo html_writer::empty_tag('input', [
    'type' => 'url',
    'id' => 'url-input',
    'name' => 'url',
    'required' => 'required',
    'class' => 'form-control',
]);
echo html_writer::tag('button', get_string('add', 'local_aiassistant'), [
    'type' => 'submit',
    'class' => 'btn btn-primary',
]);
echo html_writer::end_tag('form');
echo html_writer::end_div();

echo html_writer::end_div();

// Documents table
echo html_writer::tag('h3', get_string('managedocuments', 'local_aiassistant'));
$documents = \local_aiassistant\document_manager::get_all_documents();

if (empty($documents)) {
    echo html_writer::tag('p', 'No documents uploaded yet.');
} else {
    $table = new html_table();
    $table->head = [
        get_string('documenttitle', 'local_aiassistant'),
        get_string('sourcetype', 'local_aiassistant'),
        get_string('status', 'local_aiassistant'),
        get_string('chunks', 'local_aiassistant'),
        get_string('uploadedby', 'local_aiassistant'),
        get_string('dateuploaded', 'local_aiassistant'),
        get_string('actions', 'local_aiassistant'),
    ];

    foreach ($documents as $doc) {
        $uploader = core_user::get_user($doc->uploaderid);
        $deleteurl = new moodle_url('/local/aiassistant/manage_documents.php', [
            'action' => 'delete',
            'id' => $doc->id,
            'sesskey' => sesskey(),
        ]);

        $table->data[] = [
            $doc->title,
            $doc->sourcetype,
            get_string('status_' . $doc->status, 'local_aiassistant'),
            $doc->chunks,
            fullname($uploader),
            userdate($doc->timecreated),
            html_writer::link($deleteurl, get_string('delete'), [
                'class' => 'btn btn-danger btn-sm',
                'onclick' => 'return confirm("' . get_string('confirmdelete', 'local_aiassistant') . '");',
            ]),
        ];
    }

    echo html_writer::table($table);
}

echo $OUTPUT->footer();
