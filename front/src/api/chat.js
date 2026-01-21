// Em dev usa localhost, em produção (Docker) usa /api via Nginx proxy
const API_URL = import.meta.env.PROD ? '/api' : 'http://localhost:8000';

export async function* streamMessageFromApi(content, thread_id) {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content, thread_id }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    const chunk = decoder.decode(value, { stream: true });
    buffer += chunk;
    
    buffer = buffer.replace(/\r\n/g, '\n');
    
    const events = buffer.split('\n\n');
    buffer = events.pop();

    for (const event of events) {
      const lines = event.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6);
          if (jsonStr.trim()) {
            try {
              const data = JSON.parse(jsonStr);
              yield data;
            } catch (e) {
              console.error('[DEBUG] Parse error:', e.message, 'for:', jsonStr);
            }
          }
        }
      }
    }
  }
}

export async function uploadFilesToApi(files) {
  try {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('data', file);
    });

    const response = await fetch(`${API_URL}/chat/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error uploading files:', error);
    throw error;
  }
}

export async function triggerScrapeApi() {
  try {
    const response = await fetch(`${API_URL}/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      throw new Error(`Scrape error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error triggering scrape:', error);
    throw error;
  }
}
