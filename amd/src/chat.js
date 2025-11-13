// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Chat interface JavaScript
 *
 * @module     local_aiassistant/chat
 * @copyright  2024 AI Assistant Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

define(['jquery', 'core/ajax', 'core/notification', 'core/str'], function($, Ajax, Notification, Str) {

    var currentChatId = null;
    var backendUrl = '';
    var sesskey = '';
    var userId = 0;

    /**
     * Initialize the chat interface
     */
    var init = function(config) {
        userId = config.userid;
        currentChatId = config.chatid;
        backendUrl = config.backendurl;
        sesskey = config.sesskey;

        // Load chat history
        loadChatHistory();

        // If a chat is specified, load its messages
        if (currentChatId) {
            loadMessages(currentChatId);
        }

        // Event handlers
        $('#send-btn').on('click', sendMessage);
        $('#new-chat-btn').on('click', startNewChat);
        $('#theme-select').on('change', changeTheme);

        // Allow Enter to send (Shift+Enter for new line)
        $('#chat-input').on('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Delegate click events for chat history items
        $(document).on('click', '.chat-history-item', function() {
            var chatId = $(this).data('chatid');
            loadMessages(chatId);
            currentChatId = chatId;
            $('.chat-history-item').removeClass('active');
            $(this).addClass('active');
        });
    };

    /**
     * Load chat history
     */
    var loadChatHistory = function() {
        Ajax.call([{
            methodname: 'local_aiassistant_get_history',
            args: {},
            done: function(response) {
                renderChatHistory(response.chats);
            },
            fail: Notification.exception
        }]);

        // Alternative: Use api.php endpoint
        $.ajax({
            url: M.cfg.wwwroot + '/local/aiassistant/api.php',
            method: 'POST',
            data: {
                action: 'get_history',
                sesskey: M.cfg.sesskey
            },
            success: function(response) {
                if (response.success) {
                    renderChatHistory(response.chats);
                }
            },
            error: function() {
                Notification.alert('Error', 'Could not load chat history', 'OK');
            }
        });
    };

    /**
     * Render chat history sidebar
     */
    var renderChatHistory = function(chats) {
        var $history = $('#chat-history');
        $history.empty();

        if (!chats || chats.length === 0) {
            $history.append('<p class="text-muted">No previous chats</p>');
            return;
        }

        chats.forEach(function(chat) {
            var date = new Date(chat.timemodified * 1000);
            var dateStr = date.toLocaleDateString();
            var title = chat.title || 'New Chat';

            var $item = $('<div>')
                .addClass('chat-history-item')
                .data('chatid', chat.id)
                .attr('data-chatid', chat.id);

            if (chat.id == currentChatId) {
                $item.addClass('active');
            }

            $item.append(
                $('<div>').addClass('chat-title').text(title),
                $('<div>').addClass('chat-date').text(dateStr)
            );

            $history.append($item);
        });
    };

    /**
     * Load messages for a chat
     */
    var loadMessages = function(chatId) {
        $.ajax({
            url: M.cfg.wwwroot + '/local/aiassistant/api.php',
            method: 'POST',
            data: {
                action: 'get_messages',
                chatid: chatId,
                sesskey: M.cfg.sesskey
            },
            success: function(response) {
                if (response.success) {
                    renderMessages(response.messages);
                }
            },
            error: function() {
                Notification.alert('Error', 'Could not load messages', 'OK');
            }
        });
    };

    /**
     * Render messages in chat area
     */
    var renderMessages = function(messages) {
        var $container = $('#chat-messages');
        $container.empty();

        messages.forEach(function(message) {
            appendMessage(message.role, message.content, message.metadata);
        });

        scrollToBottom();
    };

    /**
     * Append a message to the chat
     */
    var appendMessage = function(role, content, metadata) {
        var $container = $('#chat-messages');
        var $message = $('<div>')
            .addClass('chat-message')
            .addClass('message-' + role);

        var $content = $('<div>')
            .addClass('message-content')
            .html(formatMessage(content));

        $message.append($content);

        // Add sources if available
        if (metadata && metadata.sources && metadata.sources.length > 0) {
            var $sources = $('<div>').addClass('message-sources');
            $sources.append('<strong>Sources:</strong>');
            var $sourceList = $('<ul>');
            metadata.sources.forEach(function(source) {
                $sourceList.append($('<li>').text(source));
            });
            $sources.append($sourceList);
            $message.append($sources);
        }

        $container.append($message);
        scrollToBottom();
    };

    /**
     * Format message content (basic markdown support)
     */
    var formatMessage = function(content) {
        // Basic markdown-like formatting
        content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\*(.+?)\*/g, '<em>$1</em>');
        content = content.replace(/\n/g, '<br>');
        return content;
    };

    /**
     * Send a message
     */
    var sendMessage = function() {
        var $input = $('#chat-input');
        var message = $input.val().trim();

        if (!message) {
            return;
        }

        // Disable input while processing
        $input.prop('disabled', true);
        $('#send-btn').prop('disabled', true);

        // Append user message immediately
        appendMessage('user', message, {});
        $input.val('');

        // Show thinking indicator
        var $thinking = $('<div>')
            .addClass('chat-message message-assistant thinking')
            .html('<div class="message-content"><em>Thinking...</em></div>');
        $('#chat-messages').append($thinking);
        scrollToBottom();

        // Send to backend
        $.ajax({
            url: M.cfg.wwwroot + '/local/aiassistant/api.php',
            method: 'POST',
            data: {
                action: 'chat',
                message: message,
                chatid: currentChatId || 0,
                theme: $('#theme-select').val(),
                sesskey: M.cfg.sesskey
            },
            success: function(response) {
                $thinking.remove();

                if (response.success) {
                    currentChatId = response.chatid;
                    appendMessage('assistant', response.response.content, response.response);

                    // Reload chat history if this was a new chat
                    if (!currentChatId) {
                        loadChatHistory();
                    }
                } else {
                    Notification.alert('Error', response.error || 'An error occurred', 'OK');
                }
            },
            error: function(xhr, status, error) {
                $thinking.remove();
                Notification.alert('Error', 'Could not send message: ' + error, 'OK');
            },
            complete: function() {
                $input.prop('disabled', false);
                $('#send-btn').prop('disabled', false);
                $input.focus();
            }
        });
    };

    /**
     * Start a new chat
     */
    var startNewChat = function() {
        currentChatId = null;
        $('#chat-messages').empty();
        $('.chat-history-item').removeClass('active');
        $('#chat-input').focus();
    };

    /**
     * Change theme
     */
    var changeTheme = function() {
        var theme = $(this).val();
        var $container = $('.aiassistant-container');

        // Remove all theme classes
        $container.attr('class', function(i, c) {
            return c.replace(/(^|\s)theme-\S+/g, '');
        });

        // Add new theme class
        $container.addClass('theme-' + theme);

        // Save preference
        $.ajax({
            url: M.cfg.wwwroot + '/local/aiassistant/api.php',
            method: 'POST',
            data: {
                action: 'set_setting',
                name: 'theme',
                value: theme,
                sesskey: M.cfg.sesskey
            }
        });
    };

    /**
     * Scroll chat to bottom
     */
    var scrollToBottom = function() {
        var $container = $('#chat-messages');
        $container.scrollTop($container[0].scrollHeight);
    };

    return {
        init: init
    };
});
