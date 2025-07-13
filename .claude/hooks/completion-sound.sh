#!/bin/bash
# Claude hook to play sound on completion or when input is needed

# Check if this is a completion event (when Claude finishes speaking)
if [[ "$CLAUDE_HOOK_EVENT" == "response_complete" ]]; then
    # Check if the response contains certain keywords that indicate completion or need for input
    if echo "$CLAUDE_RESPONSE" | grep -qiE "(completed|finished|ready|done|next steps|ready to continue|when you're ready|confirm|proceed|waiting for|need your|please provide|let me know)"; then
        # Play a system beep (cross-platform)
        printf '\a'
        
        # Alternative: Use speaker-test for a more noticeable sound
        # Plays a short sine wave at 1000Hz for 0.2 seconds
        if command -v speaker-test &> /dev/null; then
            timeout 0.2s speaker-test -t sine -f 1000 &> /dev/null || true
        fi
        
        # Alternative: Use paplay if available (PulseAudio)
        # if command -v paplay &> /dev/null && [[ -f /usr/share/sounds/freedesktop/stereo/complete.oga ]]; then
        #     paplay /usr/share/sounds/freedesktop/stereo/complete.oga &
        # fi
    fi
fi

# For tool completion events (when a task is done)
if [[ "$CLAUDE_HOOK_EVENT" == "tool_use_complete" ]]; then
    # Check if it's a TodoWrite tool marking something as completed
    if [[ "$CLAUDE_TOOL_NAME" == "TodoWrite" ]] && echo "$CLAUDE_TOOL_PARAMS" | grep -q '"status":"completed"'; then
        # Play a different sound for task completion
        printf '\a\a'  # Double beep
        
        # Alternative sound
        if command -v speaker-test &> /dev/null; then
            timeout 0.1s speaker-test -t sine -f 800 &> /dev/null || true
            sleep 0.1
            timeout 0.1s speaker-test -t sine -f 1200 &> /dev/null || true
        fi
    fi
fi