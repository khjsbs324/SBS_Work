async function loadPresentation() {
  const response = await fetch('./presentation.json');
  if (!response.ok) {
    throw new Error('presentation.json을 불러오지 못했습니다.');
  }
  return response.json();
}

function escapeHtml(value = '') {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}

function renderRawPage(page) {
  return `
    <section class="slide" data-page-file="${page.file}">
      <div class="slide__grid">
        <pre>${escapeHtml(page.markdown)}</pre>
      </div>
    </section>
  `;
}

async function init() {
  const root = document.querySelector('#presentation');
  const pages = await loadPresentation();
  root.innerHTML = pages.map(renderRawPage).join('');
}

init().catch((error) => {
  console.error(error);
  document.body.innerHTML = `<pre>${escapeHtml(error.message)}</pre>`;
});
