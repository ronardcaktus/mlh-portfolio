const form = document.getElementById('timeline-form');
const feed = document.getElementById('tl-feed');
const emptyMsg = document.getElementById('tl-empty');
const countEl = document.getElementById('tl-count');
const statusEl = document.getElementById('tl-status');
const submitBtn = document.getElementById('tl-submit');

// Gravatar accepts SHA-256 hashes of the normalized email
async function gravatarUrl(email) {
    const normalized = (email || '').trim().toLowerCase();
    try {
        const bytes = new TextEncoder().encode(normalized);
        const digest = await crypto.subtle.digest('SHA-256', bytes);
        const hash = Array.from(new Uint8Array(digest))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
        return `https://www.gravatar.com/avatar/${hash}?d=identicon&s=96`;
    } catch {
        // crypto.subtle needs a secure context; fall back to a generic avatar
        return 'https://www.gravatar.com/avatar/?d=mp&s=96';
    }
}

function formatDate(value) {
    const date = new Date(value);
    if (isNaN(date)) return value;
    return date.toLocaleString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: 'numeric', minute: '2-digit'
    });
}

async function renderPost(post) {
    const item = document.createElement('li');
    item.className = 'tl-post';

    const avatar = document.createElement('img');
    avatar.className = 'tl-avatar';
    avatar.alt = '';
    avatar.src = await gravatarUrl(post.email);

    const card = document.createElement('div');
    card.className = 'tl-card';

    const meta = document.createElement('div');
    meta.className = 'tl-card-meta';

    const name = document.createElement('span');
    name.className = 'tl-card-name';
    name.textContent = post.name;

    const date = document.createElement('time');
    date.className = 'tl-card-date';
    date.textContent = formatDate(post.created_at);

    const content = document.createElement('p');
    content.className = 'tl-card-content';
    content.textContent = post.content;

    meta.append(name, date);
    card.append(meta, content);
    item.append(avatar, card);
    return item;
}

function updateCount() {
    const n = feed.children.length;
    countEl.textContent = n === 1 ? '1 post' : `${n} posts`;
    emptyMsg.hidden = n > 0;
}

async function loadPosts() {
    try {
        const res = await fetch('/api/timeline_post');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const items = await Promise.all(data.timeline_posts.map(renderPost));
        feed.replaceChildren(...items);
    } catch (err) {
        emptyMsg.textContent = 'Could not load posts. Try refreshing the page.';
    }
    updateCount();
}

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    submitBtn.disabled = true;
    statusEl.classList.remove('error');
    statusEl.textContent = '';

    try {
        const res = await fetch('/api/timeline_post', {
            method: 'POST',
            body: new FormData(form)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const post = await res.json();

        const item = await renderPost(post);
        item.classList.add('tl-new');
        feed.prepend(item);
        setTimeout(() => item.classList.remove('tl-new'), 1600);
        updateCount();

        form.reset();
        statusEl.textContent = 'Posted!';
        setTimeout(() => { statusEl.textContent = ''; }, 2500);
    } catch (err) {
        statusEl.classList.add('error');
        statusEl.textContent = 'Something went wrong — please try again.';
    } finally {
        submitBtn.disabled = false;
    }
});

loadPosts();
