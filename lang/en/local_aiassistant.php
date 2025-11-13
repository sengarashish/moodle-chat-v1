<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * English language strings for local_aiassistant
 *
 * @package    local_aiassistant
 * @copyright  2024 AI Assistant Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'AI Assistant';
$string['aiassistant'] = 'AI Assistant';

// Capabilities
$string['aiassistant:use'] = 'Use AI Assistant';
$string['aiassistant:managecontent'] = 'Manage AI Assistant knowledge base';
$string['aiassistant:viewallhistory'] = 'View all users chat history';

// Settings
$string['settings'] = 'AI Assistant Settings';
$string['llmprovider'] = 'LLM Provider';
$string['llmprovider_desc'] = 'Choose the language model provider';
$string['openai'] = 'OpenAI';
$string['anthropic'] = 'Anthropic';
$string['openaiapikey'] = 'OpenAI API Key';
$string['openaiapikey_desc'] = 'Your OpenAI API key';
$string['anthropicapikey'] = 'Anthropic API Key';
$string['anthropicapikey_desc'] = 'Your Anthropic API key';
$string['backendurl'] = 'Backend URL';
$string['backendurl_desc'] = 'URL of the Python backend service';
$string['defaulttheme'] = 'Default Theme';
$string['defaulttheme_desc'] = 'Default chat UI theme';
$string['enableageresponses'] = 'Enable Age-Based Responses';
$string['enableageresponses_desc'] = 'Customize responses based on user age';
$string['serperapikey'] = 'Serper API Key';
$string['serperapikey_desc'] = 'API key for internet search (optional)';

// UI Strings
$string['chat'] = 'Chat';
$string['newchat'] = 'New Chat';
$string['chathistory'] = 'Chat History';
$string['theme'] = 'Theme';
$string['theme_default'] = 'Default';
$string['theme_jungle'] = 'Jungle';
$string['theme_ocean'] = 'Ocean';
$string['theme_space'] = 'Space';
$string['selecttheme'] = 'Select Theme';
$string['sendmessage'] = 'Send Message';
$string['typeamessage'] = 'Type a message...';
$string['thinking'] = 'Thinking...';
$string['error'] = 'Error';
$string['errorconnection'] = 'Could not connect to AI service';
$string['errormessage'] = 'An error occurred: {$a}';

// Knowledge Base
$string['knowledgebase'] = 'Knowledge Base';
$string['managedocuments'] = 'Manage Documents';
$string['uploaddocument'] = 'Upload Document';
$string['addurl'] = 'Add URL';
$string['documenttitle'] = 'Document Title';
$string['documenturl'] = 'Document URL';
$string['documentfile'] = 'Document File';
$string['upload'] = 'Upload';
$string['add'] = 'Add';
$string['status'] = 'Status';
$string['status_pending'] = 'Pending';
$string['status_processing'] = 'Processing';
$string['status_completed'] = 'Completed';
$string['status_failed'] = 'Failed';
$string['chunks'] = 'Chunks';
$string['uploadedby'] = 'Uploaded By';
$string['dateuploaded'] = 'Date Uploaded';
$string['actions'] = 'Actions';
$string['delete'] = 'Delete';
$string['confirm'] = 'Confirm';
$string['confirmdelete'] = 'Are you sure you want to delete this document?';

// Messages
$string['documentsaved'] = 'Document saved successfully';
$string['documentdeleted'] = 'Document deleted successfully';
$string['chatsaved'] = 'Chat saved';
$string['chatdeleted'] = 'Chat deleted';

// Privacy
$string['privacy:metadata:local_aiassistant_chats'] = 'Information about user chat sessions';
$string['privacy:metadata:local_aiassistant_chats:userid'] = 'The ID of the user';
$string['privacy:metadata:local_aiassistant_chats:title'] = 'The title of the chat session';
$string['privacy:metadata:local_aiassistant_chats:theme'] = 'The theme selected for the chat';
$string['privacy:metadata:local_aiassistant_messages'] = 'Chat messages';
$string['privacy:metadata:local_aiassistant_messages:content'] = 'The message content';
$string['privacy:metadata:local_aiassistant_messages:role'] = 'Whether the message is from user or assistant';
$string['privacy:metadata:local_aiassistant_settings'] = 'User settings';
$string['privacy:metadata:local_aiassistant_settings:userid'] = 'The ID of the user';
$string['privacy:metadata:local_aiassistant_settings:name'] = 'Setting name';
$string['privacy:metadata:local_aiassistant_settings:value'] = 'Setting value';
