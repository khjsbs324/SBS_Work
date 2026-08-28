(function () {
  'use strict';

  var root = document.getElementById('detail-page');
  var documentData = window.DETAIL_PAGE_DATA;

  function text(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function lines(value) {
    return text(value).replace(/\r?\n/g, '<br>');
  }

  function list(value) {
    return Array.isArray(value) ? value : [];
  }

  function fit(value) {
    return value === 'contain' ? 'contain' : 'cover';
  }

  function focal(value) {
    var candidate = String(value || 'center center');
    return /^[a-z0-9 .%+-]+$/i.test(candidate) ? candidate : 'center center';
  }

  function mediaMarkup(media, className) {
    if (!media || !media.src) {
      return '';
    }

    var classes = 'media-frame ' + (className || '');
    var style = '--media-fit:' + fit(media.fit) + ';--media-focal:' + focal(media.focal);

    return [
      '<figure class="', text(classes), '" style="', text(style), '">',
      '<img src="', text(media.src), '" alt="', text(media.alt), '" loading="eager" decoding="sync">',
      '<div class="media-fallback" aria-hidden="true"><span>', text(media.src), '</span></div>',
      '</figure>'
    ].join('');
  }

  function sectionLead(section) {
    return [
      '<header class="section-lead">',
      '<p class="section-eyebrow">', text(section.eyebrow), '</p>',
      '<h2 class="section-heading">', lines(section.heading), '</h2>',
      '<p class="section-body">', text(section.body), '</p>',
      '</header>'
    ].join('');
  }

  function shell(section, index, content) {
    var meta = section._meta || {};
    var background = meta.background || 'surface-porcelain';
    var layout = meta.layout || 'default';
    var source = meta.sourceFile || '';

    return [
      '<section class="detail-section section--', text(section.type), ' layout--', text(layout),
      '" id="', text(section.id), '" data-section-id="', text(section.id), '" data-section-type="', text(section.type),
      '" data-background="', text(background), '" data-source-file="', text(source),
      '" data-section-index="', String(index + 1).padStart(2, '0'), '">',
      content,
      '</section>'
    ].join('');
  }

  function renderHero(section, index) {
    var badges = list(section.badges).map(function (badge) {
      return '<li class="badge">' + text(badge) + '</li>';
    }).join('');

    var content = [
      '<nav class="hero-nav" aria-label="브랜드 정보">',
      '<p class="hero-brand">BRUME</p>',
      '<span class="hero-edition">FORMULA 01 · SEOUL</span>',
      '</nav>',
      '<div class="hero-copy">',
      '<p class="section-eyebrow">', text(section.eyebrow), '</p>',
      '<h1 class="hero-title">', lines(section.heading), '</h1>',
      '<p class="section-body">', text(section.body), '</p>',
      '</div>',
      mediaMarkup(section.media, 'hero-media'),
      '<div class="hero-offer">',
      '<div>',
      '<p class="hero-product-name">', text(section.productName), '</p>',
      '<p class="hero-subtitle">', text(section.subtitle), '</p>',
      '<ul class="badge-row">', badges, '</ul>',
      '</div>',
      '<div>',
      '<div class="hero-price"><strong>', text(section.price), '</strong><span>', text(section.volume), '</span></div>',
      '<a class="commerce-button" href="#benefit01">', text(section.ctaLabel), '</a>',
      '</div>',
      '</div>',
      '<p class="micro-note hero-note">', text(section.note), '</p>'
    ].join('');

    return shell(section, index, content);
  }

  function renderProblem(section, index) {
    var cards = list(section.painPoints).map(function (item) {
      return [
        '<article class="problem-card">',
        '<span class="problem-card__number">', text(item.number), '</span>',
        '<h3>', text(item.title), '</h3>',
        '<p>', text(item.copy), '</p>',
        '</article>'
      ].join('');
    }).join('');

    return shell(section, index, [
      sectionLead(section),
      '<div class="problem-cards">', cards, '</div>',
      '<blockquote class="problem-closing">', text(section.closing), '</blockquote>'
    ].join(''));
  }

  function renderBenefit(section, index) {
    var cards = list(section.benefits).map(function (item) {
      return [
        '<article class="benefit-card">',
        '<span class="benefit-card__tag">', text(item.tag), '</span>',
        '<span class="benefit-card__number" aria-hidden="true">', text(item.number), '</span>',
        '<h3>', text(item.title), '</h3>',
        '<p>', text(item.copy), '</p>',
        '</article>'
      ].join('');
    }).join('');

    return shell(section, index, [
      sectionLead(section),
      '<div class="benefit-grid">', cards, '</div>',
      '<p class="ingredient-line">', text(section.ingredientLine), '</p>'
    ].join(''));
  }

  function renderEvidence(section, index) {
    var rows = list(section.evidenceCards).map(function (item) {
      return [
        '<article class="evidence-row">',
        '<span class="evidence-code">', text(item.code), '</span>',
        '<h3 class="evidence-name">', text(item.name), '<small>', text(item.korean), '</small></h3>',
        '<div class="evidence-copy"><strong>', text(item.role), '</strong><p>', text(item.copy), '</p></div>',
        '</article>'
      ].join('');
    }).join('');

    return shell(section, index, [
      sectionLead(section),
      '<div class="evidence-ledger">', rows, '</div>',
      '<aside class="disclosure-box"><p class="micro-note">', text(section.disclosure), '</p></aside>'
    ].join(''));
  }

  function renderDetail(section, index) {
    var assets = list(section.media);
    var features = list(section.features).map(function (item) {
      return [
        '<article class="texture-feature">',
        '<h3>', text(item.title), '</h3>',
        '<p>', text(item.copy), '</p>',
        '</article>'
      ].join('');
    }).join('');

    return shell(section, index, [
      '<div class="detail-intro">',
      '<header class="section-lead">',
      '<p class="section-eyebrow">', text(section.eyebrow), '</p>',
      '<h2 class="section-heading">', lines(section.heading), '</h2>',
      '</header>',
      '<p class="section-body">', text(section.body), '</p>',
      '</div>',
      mediaMarkup(assets[0], 'texture-media'),
      '<div class="texture-features">', features, '</div>',
      '<div class="product-story">',
      mediaMarkup(assets[1], 'product-media'),
      '<div class="product-story__copy">',
      '<strong>BRUME 01<br>CERAMIDE CREAM</strong>',
      '<p class="micro-note">', text(section.caption), '</p>',
      '</div>',
      '</div>'
    ].join(''));
  }

  function renderHowTo(section, index) {
    var steps = list(section.steps).map(function (item) {
      return [
        '<article class="step-item">',
        '<span class="step-number">', text(item.number), '</span>',
        '<h3>', text(item.title), '</h3>',
        '<p>', text(item.copy), '</p>',
        '</article>'
      ].join('');
    }).join('');

    return shell(section, index, [
      sectionLead(section),
      '<div class="step-flow">', steps, '</div>',
      '<aside class="tip-box"><strong>ROUTINE TIP</strong><p>', text(section.tip), '</p></aside>'
    ].join(''));
  }

  function renderSpec(section, index) {
    var rows = list(section.specifications).map(function (item) {
      return '<div class="spec-row"><dt>' + text(item.label) + '</dt><dd>' + text(item.value) + '</dd></div>';
    }).join('');

    return shell(section, index, [
      sectionLead(section),
      '<dl class="spec-table">', rows, '</dl>',
      '<aside class="notice-box"><strong>USE WITH CARE</strong><p class="micro-note">', text(section.notice), '</p></aside>'
    ].join(''));
  }

  function renderFaq(section, index) {
    var items = list(section.items).map(function (item, itemIndex) {
      return [
        '<article class="faq-item">',
        '<span class="faq-index">Q', String(itemIndex + 1).padStart(2, '0'), '</span>',
        '<h3>', text(item.question), '</h3>',
        '<p>', text(item.answer), '</p>',
        '</article>'
      ].join('');
    }).join('');

    return shell(section, index, [
      sectionLead(section),
      '<div class="faq-list">', items, '</div>'
    ].join(''));
  }

  function renderCta(section, index) {
    var points = list(section.summaryPoints).map(function (point) {
      return '<li>' + text(point) + '</li>';
    }).join('');

    return shell(section, index, [
      sectionLead(section),
      '<div class="cta-product">',
      mediaMarkup(section.media, 'cta-product-media'),
      '<div class="cta-product-copy">',
      '<p class="cta-product-name">', text(section.productName), '</p>',
      '<div class="cta-price"><strong>', text(section.price), '</strong><span>', text(section.volume), '</span></div>',
      '<ul class="cta-points">', points, '</ul>',
      '<a class="commerce-button commerce-button--light cta-button" href="#hero01">', text(section.ctaLabel), '</a>',
      '</div>',
      '</div>',
      '<p class="micro-note cta-legal">', text(section.legal), '</p>'
    ].join(''));
  }

  var renderers = {
    hero: renderHero,
    problem: renderProblem,
    benefit: renderBenefit,
    evidence: renderEvidence,
    detail: renderDetail,
    'how-to': renderHowTo,
    spec: renderSpec,
    faq: renderFaq,
    cta: renderCta
  };

  function watchAssets() {
    var images = root.querySelectorAll('.media-frame img');
    images.forEach(function (image) {
      var frame = image.closest('.media-frame');

      function loaded() {
        frame.classList.remove('is-missing');
        frame.classList.add('is-loaded');
      }

      function missing() {
        frame.classList.remove('is-loaded');
        frame.classList.add('is-missing');
      }

      image.addEventListener('load', loaded, { once: true });
      image.addEventListener('error', missing, { once: true });

      if (image.complete) {
        if (image.naturalWidth > 0) {
          loaded();
        } else {
          missing();
        }
      }
    });
  }

  function init() {
    if (!root) {
      throw new Error('detail-page root를 찾을 수 없습니다.');
    }

    if (!documentData || !Array.isArray(documentData.sections)) {
      throw new Error('detail-page-data.js가 없거나 sections 데이터가 유효하지 않습니다.');
    }

    root.innerHTML = documentData.sections.map(function (section, index) {
      var renderer = renderers[section.type];
      if (!renderer) {
        throw new Error('지원하지 않는 section type: ' + section.type);
      }
      return renderer(section, index);
    }).join('');

    watchAssets();
    if (window.location.hash) {
      var targetId = decodeURIComponent(window.location.hash.slice(1));
      var target = document.getElementById(targetId);
      if (target) {
        target.scrollIntoView({ block: 'start' });
      }
    }
    document.documentElement.classList.add('is-ready');
    window.__DETAIL_PAGE_READY__ = true;
  }

  try {
    init();
  } catch (error) {
    console.error(error);
    root.innerHTML = '<div class="loading-state" role="alert">' + text(error.message) + '</div>';
    window.__DETAIL_PAGE_READY__ = false;
  }
}());
