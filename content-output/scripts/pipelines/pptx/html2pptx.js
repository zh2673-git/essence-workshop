/**
 * 本质工坊 · html2pptx.js
 * 基于 huashu-design 的 html2pptx 核心逻辑移植
 *
 * 功能：读取 HTML 幻灯片 DOM → 提取元素位置/样式 → 生成精确的 PPTX 文件
 *
 * 依赖：playwright, pptxgenjs
 *
 * 用法：
 *   node html2pptx.js <input.html> <output.pptx> [--layout LAYOUT_16x9|LAYOUT_4x3]
 */

const { chromium } = require('playwright');
const pptxgen = require('pptxgenjs');
const path = require('path');
const fs = require('fs');

const LAYOUTS = {
  LAYOUT_16x9: { width: 13.33, height: 7.5 },
  LAYOUT_4x3: { width: 10, height: 7.5 },
};

const EMU_PER_INCH = 914400;
const PT_PER_INCH = 72;

function parseArgs() {
  const args = process.argv.slice(2);
  const positional = [];
  let layout = 'LAYOUT_16x9';

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--layout' && args[i + 1]) {
      layout = args[i + 1];
      i++;
    } else {
      positional.push(args[i]);
    }
  }

  if (positional.length < 2) {
    console.error('Usage: node html2pptx.js <input.html> <output.pptx> [--layout LAYOUT_16x9|LAYOUT_4x3]');
    process.exit(1);
  }

  return { input: positional[0], output: positional[1], layout };
}

async function extractSlideData(page) {
  return await page.evaluate(() => {
    const slides = document.querySelectorAll('.slide-page, [data-slide], section[class*="slide"]');
    const slideDataList = [];

    if (slides.length === 0) {
      const bodyElements = document.querySelectorAll('body > *:not(script):not(style)');
      if (bodyElements.length > 0) {
        slideDataList.push(extractElementsFromContainer(document.body));
      }
      return slideDataList;
    }

    slides.forEach((slide, slideIndex) => {
      const data = extractElementsFromContainer(slide);
      data.slideIndex = slideIndex;
      data.pageType = slide.dataset.pageType || slide.dataset.slideType || 'default';
      slideDataList.push(data);
    });

    function extractElementsFromContainer(container) {
      const elements = [];
      const containerRect = container.getBoundingClientRect();
      const containerWidth = containerRect.width;
      const containerHeight = containerRect.height;

      const walk = (node) => {
        if (node.nodeType !== Node.ELEMENT_NODE) return;
        if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE') return;
        if (node.classList.contains('nav-bar') || node.classList.contains('sidebar-nav') || node.classList.contains('keyboard-hint')) return;

        const style = window.getComputedStyle(node);
        const rect = node.getBoundingClientRect();

        if (rect.width === 0 || rect.height === 0) return;

        const hasDirectText = Array.from(node.childNodes).some(
          child => child.nodeType === Node.TEXT_NODE && child.textContent.trim().length > 0
        );

        const isPlaceholder = node.classList.contains('placeholder');
        const isMerged = node.hasAttribute('data-pptx-merge');

        if (node.tagName === 'IMG' || node.tagName === 'SVG') {
          const x = ((rect.left - containerRect.left) / containerWidth) * 100;
          const y = ((rect.top - containerRect.top) / containerHeight) * 100;
          const w = (rect.width / containerWidth) * 100;
          const h = (rect.height / containerHeight) * 100;

          if (node.tagName === 'IMG') {
            elements.push({
              type: 'image',
              src: node.src || node.getAttribute('src'),
              x, y, w, h,
              borderRadius: parseFloat(style.borderRadius) || 0,
              shadow: style.boxShadow !== 'none' ? style.boxShadow : null,
            });
          } else {
            const svgData = new XMLSerializer().serializeToString(node);
            elements.push({
              type: 'svg',
              svgData,
              x, y, w, h,
            });
          }
          return;
        }

        if (hasDirectText || isMerged) {
          const textContent = isMerged
            ? Array.from(node.querySelectorAll('p, li, span, h1, h2, h3, h4, h5, h6'))
                .map(el => el.textContent.trim())
                .filter(t => t.length > 0)
                .join('\n')
            : node.textContent.trim();

          if (!textContent) return;

          const x = ((rect.left - containerRect.left) / containerWidth) * 100;
          const y = ((rect.top - containerRect.top) / containerHeight) * 100;
          const w = (rect.width / containerWidth) * 100;
          const h = (rect.height / containerHeight) * 100;

          const fontSize = parseFloat(style.fontSize) || 16;
          const fontWeight = style.fontWeight;
          const isBold = fontWeight === 'bold' || parseInt(fontWeight) >= 600;
          const isItalic = style.fontStyle === 'italic';
          const color = style.color;
          const textAlign = style.textAlign || 'left';
          const rotation = parseFloat(style.transform?.replace(/[^0-9.-]/g, '')) || 0;

          elements.push({
            type: 'text',
            text: textContent,
            x, y, w, h,
            fontSize,
            isBold,
            isItalic,
            color,
            textAlign,
            rotation,
            fontFamily: style.fontFamily,
            isMerged,
            isPlaceholder,
            lineHeight: parseFloat(style.lineHeight) || 1.5,
          });
          return;
        }

        if (style.backgroundColor && style.backgroundColor !== 'rgba(0, 0, 0, 0)' && style.backgroundColor !== 'transparent') {
          const x = ((rect.left - containerRect.left) / containerWidth) * 100;
          const y = ((rect.top - containerRect.top) / containerHeight) * 100;
          const w = (rect.width / containerWidth) * 100;
          const h = (rect.height / containerHeight) * 100;

          elements.push({
            type: 'shape',
            shapeType: 'rect',
            x, y, w, h,
            fill: style.backgroundColor,
            borderRadius: parseFloat(style.borderRadius) || 0,
            border: style.border !== 'none' ? {
              color: style.borderColor,
              width: parseFloat(style.borderWidth) || 0,
            } : null,
          });
        }

        Array.from(node.children).forEach(child => walk(child));
      };

      Array.from(container.children).forEach(child => walk(child));

      const bgStyle = window.getComputedStyle(container);
      const background = bgStyle.backgroundImage !== 'none' ? bgStyle.backgroundImage : null;
      const bgColor = bgStyle.backgroundColor !== 'rgba(0, 0, 0, 0)' && bgStyle.backgroundColor !== 'transparent'
        ? bgStyle.backgroundColor : null;

      return {
        elements,
        containerWidth,
        containerHeight,
        background,
        bgColor,
      };
    }

    return slideDataList;
  });
}

function cssColorToHex(cssColor) {
  if (!cssColor) return '000000';
  if (cssColor.startsWith('#')) return cssColor.replace('#', '');
  const match = cssColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (match) {
    const r = parseInt(match[1]).toString(16).padStart(2, '0');
    const g = parseInt(match[2]).toString(16).padStart(2, '0');
    const b = parseInt(match[3]).toString(16).padStart(2, '0');
    return r + g + b;
  }
  return '000000';
}

function addElements(slideData, targetSlide, pres) {
  const layout = pres.layout;
  const slideWidth = layout === 'LAYOUT_4x3' ? 10 : 13.33;
  const slideHeight = 7.5;

  if (slideData.bgColor) {
    targetSlide.background = { color: cssColorToHex(slideData.bgColor) };
  }

  if (slideData.background && slideData.background.includes('gradient')) {
    const colorMatch = slideData.background.match(/#[0-9a-fA-F]{6}|rgba?\([^)]+\)/g);
    if (colorMatch && colorMatch.length >= 2) {
      targetSlide.background = {
        fill: { type: 'solid', color: cssColorToHex(colorMatch[0]) },
      };
    }
  }

  for (const el of slideData.elements) {
    try {
      const x = (el.x / 100) * slideWidth;
      const y = (el.y / 100) * slideHeight;
      const w = (el.w / 100) * slideWidth;
      const h = (el.h / 100) * slideHeight;

      if (el.type === 'text') {
        const fontSize = Math.max(8, el.fontSize * 0.75);
        const textOpts = {
          x,
          y,
          w: Math.max(0.5, w),
          h: Math.max(0.3, h),
          fontSize,
          color: cssColorToHex(el.color),
          bold: el.isBold,
          italic: el.isItalic,
          align: el.textAlign === 'center' ? 'center' : el.textAlign === 'right' ? 'right' : 'left',
          valign: 'top',
          fontFace: el.fontFamily?.split(',')[0]?.replace(/"/g, '').trim() || 'Microsoft YaHei',
          lineSpacingMultiple: el.lineHeight || 1.5,
        };

        if (el.rotation) {
          textOpts.rotate = el.rotation;
        }

        if (el.isMerged || el.text.includes('\n')) {
          const lines = el.text.split('\n');
          const textRows = lines.map(line => ({
            text: line,
            options: { fontSize, bold: el.isBold, italic: el.isItalic, color: cssColorToHex(el.color) },
          }));
          targetSlide.addText(textRows, textOpts);
        } else {
          targetSlide.addText(el.text, textOpts);
        }
      }

      else if (el.type === 'image') {
        const imgOpts = {
          x,
          y,
          w: Math.max(0.5, w),
          h: Math.max(0.3, h),
        };
        if (el.borderRadius > 0) {
          imgOpts.rounding = true;
        }
        try {
          if (el.src && (el.src.startsWith('http') || el.src.startsWith('file://') || el.src.startsWith('data:'))) {
            targetSlide.addImage({ ...imgOpts, path: el.src });
          }
        } catch (imgErr) {
          console.warn(`  Warning: Could not add image: ${imgErr.message}`);
        }
      }

      else if (el.type === 'svg') {
        const svgOpts = {
          x,
          y,
          w: Math.max(0.5, w),
          h: Math.max(0.3, h),
        };
        try {
          const svgBase64 = Buffer.from(el.svgData).toString('base64');
          targetSlide.addImage({
            ...svgOpts,
            data: `image/svg+xml;base64,${svgBase64}`,
          });
        } catch (svgErr) {
          console.warn(`  Warning: Could not add SVG: ${svgErr.message}`);
        }
      }

      else if (el.type === 'shape') {
        const shapeOpts = {
          x,
          y,
          w: Math.max(0.1, w),
          h: Math.max(0.1, h),
          fill: { color: cssColorToHex(el.fill) },
          rectRadius: el.borderRadius ? el.borderRadius / 10 : 0,
        };
        if (el.border) {
          shapeOpts.line = {
            color: cssColorToHex(el.border.color),
            width: el.border.width,
          };
        }
        targetSlide.addShape(pres.shapes.RECTANGLE, shapeOpts);
      }
    } catch (elErr) {
      console.warn(`  Warning: Could not add element: ${elErr.message}`);
    }
  }
}

async function main() {
  const { input, output, layout: layoutName } = parseArgs();

  if (!LAYOUTS[layoutName]) {
    console.error(`Unknown layout: ${layoutName}. Available: ${Object.keys(LAYOUTS).join(', ')}`);
    process.exit(1);
  }

  const inputPath = path.resolve(input);
  const outputPath = path.resolve(output);

  if (!fs.existsSync(inputPath)) {
    console.error(`Input file not found: ${inputPath}`);
    process.exit(1);
  }

  console.log(`[html2pptx] Starting...`);
  console.log(`  Input: ${inputPath}`);
  console.log(`  Output: ${outputPath}`);
  console.log(`  Layout: ${layoutName}`);

  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    const layout = LAYOUTS[layoutName];
    await page.setViewportSize({
      width: Math.round(layout.width * 96),
      height: Math.round(layout.height * 96),
    });

    const fileUrl = `file:///${inputPath.replace(/\\/g, '/')}`;
    await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(500);

    console.log('  Extracting slide data...');
    const slideDataList = await extractSlideData(page);
    console.log(`  Found ${slideDataList.length} slide(s)`);

    const pres = new pptxgen();
    pres.layout = layoutName;
    pres.author = 'Essence Workshop';
    pres.title = path.basename(inputPath, '.html');

    for (const slideData of slideDataList) {
      const slide = pres.addSlide();
      addElements(slideData, slide, pres);
    }

    await pres.writeFile({ fileName: outputPath });
    console.log(`  Output saved: ${outputPath}`);
    console.log(`[html2pptx] Done.`);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

main();
