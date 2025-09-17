(() => {
  const root = document.getElementById('chat-widget-root');

  let minimized = true;

  function createMinimized() {
    root.innerHTML = '';
    const btn = document.createElement('div');
    btn.className = 'chat-minimized';
    btn.innerText = 'Chat';
    btn.onclick = () => { minimized = false; renderWidget(); };
    root.appendChild(btn);
  }

  function renderWidget() {
    root.innerHTML = '';
    const widget = document.createElement('div');
    widget.className = 'chat-widget';

    const header = document.createElement('div'); header.className='chat-header';
    const title = document.createElement('div'); title.className='title'; title.innerText='Sales Assistant';
    const close = document.createElement('button'); close.innerText='✕'; close.style.marginLeft='auto'; close.onclick = () => { minimized=true; createMinimized(); };
    header.appendChild(title); header.appendChild(close);

    const messages = document.createElement('div'); messages.className='chat-messages';

    const inputWrap = document.createElement('div'); inputWrap.className='chat-input';
    const input = document.createElement('input'); input.placeholder='Type your question...';
    const btn = document.createElement('button'); btn.innerText='Send';

    inputWrap.appendChild(input); inputWrap.appendChild(btn);

    widget.appendChild(header); widget.appendChild(messages); widget.appendChild(inputWrap);
    root.appendChild(widget);

    addAssistantMessage(messages, 'Hi! I\'m here to help. How can I assist you with our services today?');

    btn.onclick = () => { sendMessage(input, messages); };
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(input, messages); });
  }

  function addUserMessage(container, text) {
    const el = document.createElement('div'); el.className='msg user'; el.innerText = text; container.appendChild(el); container.scrollTop = container.scrollHeight;
  }
  function addAssistantMessage(container, text) {
    const el = document.createElement('div'); el.className='msg assistant'; el.innerText = text; container.appendChild(el); container.scrollTop = container.scrollHeight;
  }

  async function sendMessage(input, messages) {
    const val = input.value.trim();
    if (!val) return;
    addUserMessage(messages, val);
    input.value = '';
    addAssistantMessage(messages, 'Typing...');

    try {
      const resp = await fetch('/chat', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: val, session_id: 'demo_session', website_context: window.WEBSITE_CONTEXT })
      });
      const data = await resp.json();
      const typing = Array.from(messages.querySelectorAll('.msg.assistant')).pop();
      if (typing) typing.remove();

      if (data.error) {
        addAssistantMessage(messages, 'Error: ' + data.error);
        return;
      }
      addAssistantMessage(messages, data.reply || 'Sorry, I had trouble answering that.');

      if (data.capture_contact) {
        const contactPrompt = document.createElement('div'); contactPrompt.className='msg assistant';
        contactPrompt.innerHTML = 'It seems you\'re interested — may I get your name, email, and phone so our sales rep can reach out?';
        messages.appendChild(contactPrompt);
      }

    } catch (err) {
      addAssistantMessage(messages, 'Network error: ' + err.message);
    }
  }

  createMinimized();
})();
