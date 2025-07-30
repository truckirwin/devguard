import JSZip from 'jszip';
import { SlideContent } from '../types/ppt';

export interface TextRun {
  text: string;
  formatting?: {
    bold?: boolean;
    italic?: boolean;
    underline?: boolean;
    fontSize?: number;
    fontFamily?: string;
    color?: string;
  };
}

export interface ParsedParagraph {
  runs: TextRun[];
  bulletType?: 'none' | 'bullet' | 'number' | 'custom';
  bulletChar?: string;
  bulletNumber?: number;
  indentLevel: number;
  alignment?: 'left' | 'center' | 'right' | 'justify';
}

export interface TextShape {
  type: 'title' | 'content' | 'placeholder' | 'textbox' | 'table';
  placeholder?: string;
  paragraphs: ParsedParagraph[];
  position?: { x: number; y: number; width: number; height: number };
}

export class AdvancedPptParser {
  private zip: JSZip | null = null;
  private slideLayouts: Map<string, any> = new Map();
  private slideMasters: Map<string, any> = new Map();
  
  async parseFile(file: File): Promise<SlideContent[]> {
    this.zip = new JSZip();
    const contents = await this.zip.loadAsync(file);
    
    // First, load slide layouts and masters for context
    await this.loadSlideLayouts(contents);
    await this.loadSlideMasters(contents);
    
    // Get all slide files
    const slideFiles = Object.keys(contents.files).filter(name => 
      name.startsWith('ppt/slides/slide') && name.endsWith('.xml')
    );
    
    // Sort slides by number
    slideFiles.sort((a, b) => {
      const numA = parseInt(a.match(/slide(\d+)\.xml/)?.[1] || '0');
      const numB = parseInt(b.match(/slide(\d+)\.xml/)?.[1] || '0');
      return numA - numB;
    });
    
    const slides: SlideContent[] = [];
    
    // Process each slide with advanced parsing
    for (const slideFile of slideFiles) {
      const slideContent = await contents.files[slideFile].async('text');
      const slideNumber = parseInt(slideFile.match(/slide(\d+)\.xml/)?.[1] || '0');
      
      const parsedSlide = await this.parseSlideXML(slideContent, slideNumber, contents);
      slides.push(parsedSlide);
    }
    
    return slides;
  }
  
  // New method to extract text shapes for preview generation
  async extractAllTextShapes(file: File): Promise<TextShape[][]> {
    this.zip = new JSZip();
    const contents = await this.zip.loadAsync(file);
    
    // Load slide layouts and masters for context
    await this.loadSlideLayouts(contents);
    await this.loadSlideMasters(contents);
    
    // Get all slide files
    const slideFiles = Object.keys(contents.files).filter(name => 
      name.startsWith('ppt/slides/slide') && name.endsWith('.xml')
    );
    
    // Sort slides by number
    slideFiles.sort((a, b) => {
      const numA = parseInt(a.match(/slide(\d+)\.xml/)?.[1] || '0');
      const numB = parseInt(b.match(/slide(\d+)\.xml/)?.[1] || '0');
      return numA - numB;
    });
    
    const shapesPerSlide: TextShape[][] = [];
    
    // Process each slide to extract shapes
    for (const slideFile of slideFiles) {
      const slideContent = await contents.files[slideFile].async('text');
      const doc = this.parseXMLToDOM(slideContent);
      const textShapes = this.extractTextShapes(doc);
      shapesPerSlide.push(textShapes);
    }
    
    return shapesPerSlide;
  }
  
  private async loadSlideLayouts(contents: JSZip) {
    const layoutFiles = Object.keys(contents.files).filter(name => 
      name.startsWith('ppt/slideLayouts/') && name.endsWith('.xml')
    );
    
    for (const layoutFile of layoutFiles) {
      const layoutContent = await contents.files[layoutFile].async('text');
      const layoutId = layoutFile.match(/slideLayout(\d+)\.xml/)?.[1];
      if (layoutId) {
        this.slideLayouts.set(layoutId, this.parseXMLToDOM(layoutContent));
      }
    }
  }
  
  private async loadSlideMasters(contents: JSZip) {
    const masterFiles = Object.keys(contents.files).filter(name => 
      name.startsWith('ppt/slideMasters/') && name.endsWith('.xml')
    );
    
    for (const masterFile of masterFiles) {
      const masterContent = await contents.files[masterFile].async('text');
      const masterId = masterFile.match(/slideMaster(\d+)\.xml/)?.[1];
      if (masterId) {
        this.slideMasters.set(masterId, this.parseXMLToDOM(masterContent));
      }
    }
  }
  
  private parseXMLToDOM(xmlString: string): Document {
    const parser = new DOMParser();
    return parser.parseFromString(xmlString, 'text/xml');
  }
  
  private async parseSlideXML(xml: string, slideNumber: number, contents: JSZip): Promise<SlideContent> {
    const doc = this.parseXMLToDOM(xml);
    const textShapes = this.extractTextShapes(doc);
    
    // Separate title and content
    const titleShape = textShapes.find(shape => 
      shape.type === 'title' || 
      shape.placeholder?.toLowerCase().includes('title')
    );
    
    const contentShapes = textShapes.filter(shape => 
      shape.type !== 'title' && 
      !shape.placeholder?.toLowerCase().includes('title')
    );
    
    // Extract speaker notes
    const notesFile = `ppt/notesSlides/notesSlide${slideNumber}.xml`;
    let speakerNotes = '';
    if (contents.files[notesFile]) {
      const notesContent = await contents.files[notesFile].async('text');
      speakerNotes = this.parseNotesXML(notesContent);
    }
    
    // Extract table content
    const tableContent = this.extractTableContent(doc);
    
    // Extract chart content  
    const chartContent = this.extractChartContent(doc);
    
    // Extract images and alt text
    const altText = this.extractComprehensiveAltText(doc);
    
    return {
      slideNumber,
      title: this.formatTextShapeContent(titleShape),
      content: this.assembleSlideContent(contentShapes, tableContent, chartContent),
      altText,
      speakerNotes
    };
  }
  
  private extractTextShapes(doc: Document): TextShape[] {
    const shapes: TextShape[] = [];
    
    // Find all shape elements (p:sp)
    const shapeElements = doc.querySelectorAll('p\\:sp, sp');
    
    for (let i = 0; i < shapeElements.length; i++) {
      const shapeElement = shapeElements[i];
      const textShape = this.parseTextShape(shapeElement);
      if (textShape && textShape.paragraphs.length > 0) {
        shapes.push(textShape);
      }
    }
    
    return shapes;
  }
  
  private parseTextShape(shapeElement: Element): TextShape | null {
    // Determine shape type and placeholder
    const nvSpPr = shapeElement.querySelector('p\\:nvSpPr, nvSpPr');
    const cNvPr = nvSpPr?.querySelector('p\\:cNvPr, cNvPr');
    const nvPr = nvSpPr?.querySelector('p\\:nvPr, nvPr');
    
    const shapeName = cNvPr?.getAttribute('name') || '';
    const phType = nvPr?.querySelector('p\\:ph, ph')?.getAttribute('type') || '';
    
    let shapeType: TextShape['type'] = 'content';
    if (shapeName.toLowerCase().includes('title') || phType === 'title' || phType === 'ctrTitle') {
      shapeType = 'title';
    } else if (phType === 'body' || phType === 'obj') {
      shapeType = 'content';
    } else if (shapeName.toLowerCase().includes('placeholder')) {
      shapeType = 'placeholder';
    } else if (shapeElement.querySelector('a\\:tbl, tbl')) {
      shapeType = 'table';
    }
    
    // Extract text body
    const txBody = shapeElement.querySelector('p\\:txBody, txBody') || 
                   shapeElement.querySelector('a\\:txBody, txBody');
    
    if (!txBody) return null;
    
    const paragraphs = this.parseTextBodyParagraphs(txBody);
    
    // Extract position if available
    const spPr = shapeElement.querySelector('p\\:spPr, spPr');
    const xfrm = spPr?.querySelector('a\\:xfrm, xfrm');
    let position;
    if (xfrm) {
      const off = xfrm.querySelector('a\\:off, off');
      const ext = xfrm.querySelector('a\\:ext, ext');
      if (off && ext) {
        position = {
          x: parseInt(off.getAttribute('x') || '0'),
          y: parseInt(off.getAttribute('y') || '0'),
          width: parseInt(ext.getAttribute('cx') || '0'),
          height: parseInt(ext.getAttribute('cy') || '0')
        };
      }
    }
    
    return {
      type: shapeType,
      placeholder: phType || undefined,
      paragraphs,
      position
    };
  }
  
  private parseTextBodyParagraphs(txBody: Element): ParsedParagraph[] {
    const paragraphs: ParsedParagraph[] = [];
    const pElements = txBody.querySelectorAll('a\\:p, p');
    
    for (let i = 0; i < pElements.length; i++) {
      const pElement = pElements[i];
      const paragraph = this.parseParagraph(pElement);
      paragraphs.push(paragraph);
    }
    
    return paragraphs;
  }
  
  private parseParagraph(pElement: Element): ParsedParagraph {
    const runs: TextRun[] = [];
    
    // Parse paragraph properties for bullets and indentation
    const pPr = pElement.querySelector('a\\:pPr, pPr');
    const bulletInfo = this.parseBulletProperties(pPr);
    const indentLevel = this.parseIndentLevel(pPr);
    const alignment = this.parseAlignment(pPr);
    
    // Parse text runs (a:r elements)
    const runElements = pElement.querySelectorAll('a\\:r, r');
    
    if (runElements.length === 0) {
      // Check for direct text in a:t elements
      const textElements = pElement.querySelectorAll('a\\:t, t');
      for (let i = 0; i < textElements.length; i++) {
        const textElement = textElements[i];
        const text = textElement.textContent || '';
        if (text.trim()) {
          runs.push({ text });
        }
      }
    } else {
      for (let i = 0; i < runElements.length; i++) {
        const runElement = runElements[i];
        const textRun = this.parseTextRun(runElement);
        if (textRun) {
          runs.push(textRun);
        }
      }
    }
    
    // Handle field elements (a:fld) for dynamic text
    const fieldElements = pElement.querySelectorAll('a\\:fld, fld');
    for (let i = 0; i < fieldElements.length; i++) {
      const fieldElement = fieldElements[i];
      const textElement = fieldElement.querySelector('a\\:t, t');
      if (textElement) {
        const text = textElement.textContent || '';
        if (text.trim()) {
          runs.push({ text });
        }
      }
    }
    
    return {
      runs,
      bulletType: bulletInfo.type,
      bulletChar: bulletInfo.char,
      bulletNumber: bulletInfo.number,
      indentLevel,
      alignment
    };
  }
  
  private parseTextRun(runElement: Element): TextRun | null {
    const textElement = runElement.querySelector('a\\:t, t');
    if (!textElement) return null;
    
    const text = textElement.textContent || '';
    if (!text) return null;
    
    // Parse run properties for formatting
    const rPr = runElement.querySelector('a\\:rPr, rPr');
    const formatting = this.parseRunProperties(rPr);
    
    return { text, formatting };
  }
  
  private parseRunProperties(rPr: Element | null): TextRun['formatting'] {
    if (!rPr) return undefined;
    
    const formatting: TextRun['formatting'] = {};
    
    // Check for bold
    if (rPr.getAttribute('b') === '1') {
      formatting.bold = true;
    }
    
    // Check for italic
    if (rPr.getAttribute('i') === '1') {
      formatting.italic = true;
    }
    
    // Check for underline
    const u = rPr.getAttribute('u');
    if (u && u !== 'none') {
      formatting.underline = true;
    }
    
    // Check for font size
    const sz = rPr.getAttribute('sz');
    if (sz) {
      formatting.fontSize = parseInt(sz) / 100; // PowerPoint uses centpoints
    }
    
    // Check for font family
    const latin = rPr.querySelector('a\\:latin, latin');
    if (latin) {
      formatting.fontFamily = latin.getAttribute('typeface') || undefined;
    }
    
    // Check for color
    const solidFill = rPr.querySelector('a\\:solidFill, solidFill');
    if (solidFill) {
      const srgbClr = solidFill.querySelector('a\\:srgbClr, srgbClr');
      if (srgbClr) {
        formatting.color = `#${srgbClr.getAttribute('val')}`;
      }
    }
    
    return Object.keys(formatting).length > 0 ? formatting : undefined;
  }
  
  private parseBulletProperties(pPr: Element | null): { type: ParsedParagraph['bulletType']; char?: string; number?: number } {
    if (!pPr) return { type: 'none' };
    
    // Check for custom bullet character
    const buChar = pPr.querySelector('a\\:buChar, buChar');
    if (buChar) {
      return {
        type: 'custom',
        char: buChar.getAttribute('char') || '•'
      };
    }
    
    // Check for auto numbering
    const buAutoNum = pPr.querySelector('a\\:buAutoNum, buAutoNum');
    if (buAutoNum) {
      const startAt = buAutoNum.getAttribute('startAt');
      return {
        type: 'number',
        number: startAt ? parseInt(startAt) : 1
      };
    }
    
    // Check for bullet font (indicates bullet points)
    const buFont = pPr.querySelector('a\\:buFont, buFont');
    const buSzPct = pPr.querySelector('a\\:buSzPct, buSzPct');
    if (buFont || buSzPct) {
      return { type: 'bullet' };
    }
    
    // Check for buNone (explicitly no bullet)
    const buNone = pPr.querySelector('a\\:buNone, buNone');
    if (buNone) {
      return { type: 'none' };
    }
    
    return { type: 'none' };
  }
  
  private parseIndentLevel(pPr: Element | null): number {
    if (!pPr) return 0;
    
    const marL = pPr.getAttribute('marL');
    if (marL) {
      // PowerPoint uses EMUs (English Metric Units)
      // 457200 EMUs = 1 inch = typical first indent level
      return Math.floor(parseInt(marL) / 457200);
    }
    
    const lvl = pPr.getAttribute('lvl');
    if (lvl) {
      return parseInt(lvl);
    }
    
    return 0;
  }
  
  private parseAlignment(pPr: Element | null): ParsedParagraph['alignment'] {
    if (!pPr) return 'left';
    
    const algn = pPr.getAttribute('algn');
    switch (algn) {
      case 'ctr': return 'center';
      case 'r': return 'right';
      case 'just': return 'justify';
      default: return 'left';
    }
  }
  
  private extractTableContent(doc: Document): string {
    const tables: string[] = [];
    const tableElements = doc.querySelectorAll('a\\:tbl, tbl');
    
    for (let i = 0; i < tableElements.length; i++) {
      const table = tableElements[i];
      const tableText = this.parseTable(table);
      if (tableText) {
        tables.push(tableText);
      }
    }
    
    return tables.join('\n\n');
  }
  
  private parseTable(table: Element): string {
    const rows: string[] = [];
    const trElements = table.querySelectorAll('a\\:tr, tr');
    
    for (let i = 0; i < trElements.length; i++) {
      const tr = trElements[i];
      const cells: string[] = [];
      const tcElements = tr.querySelectorAll('a\\:tc, tc');
      
      for (let j = 0; j < tcElements.length; j++) {
        const tc = tcElements[j];
        const txBody = tc.querySelector('a\\:txBody, txBody');
        if (txBody) {
          const paragraphs = this.parseTextBodyParagraphs(txBody);
          const cellText = this.formatParagraphs(paragraphs);
          cells.push(cellText || '');
        } else {
          cells.push('');
        }
      }
      
      if (cells.length > 0) {
        rows.push('| ' + cells.join(' | ') + ' |');
      }
    }
    
    return rows.join('\n');
  }
  
  private extractChartContent(doc: Document): string {
    const charts: string[] = [];
    
    // Look for chart references and titles
    const chartElements = doc.querySelectorAll('c\\:chart, chart');
    for (let i = 0; i < chartElements.length; i++) {
      const chart = chartElements[i];
      const title = chart.querySelector('c\\:title, title');
      if (title) {
        const titleText = this.extractTextFromElement(title);
        if (titleText) {
          charts.push(`Chart: ${titleText}`);
        }
      }
    }
    
    return charts.join('\n');
  }
  
  private extractComprehensiveAltText(doc: Document): string[] {
    const altTexts: string[] = [];
    
    // Look for alt text in various places
    const descriptors = [
      'descr',
      'title',
      'name'
    ];
    
    for (const attr of descriptors) {
      const elements = doc.querySelectorAll(`[${attr}]`);
      for (let i = 0; i < elements.length; i++) {
        const element = elements[i];
        const text = element.getAttribute(attr);
        if (text && text.trim() && !altTexts.includes(text.trim())) {
          altTexts.push(text.trim());
        }
      }
    }
    
    // Look for image descriptions
    const picElements = doc.querySelectorAll('pic\\:pic, pic');
    for (let i = 0; i < picElements.length; i++) {
      const pic = picElements[i];
      const cNvPr = pic.querySelector('pic\\:cNvPr, cNvPr');
      if (cNvPr) {
        const name = cNvPr.getAttribute('name');
        const descr = cNvPr.getAttribute('descr');
        if (name && !altTexts.includes(name)) altTexts.push(name);
        if (descr && !altTexts.includes(descr)) altTexts.push(descr);
      }
    }
    
    return altTexts;
  }
  
  private parseNotesXML(xml: string): string {
    const doc = this.parseXMLToDOM(xml);
    const textShapes = this.extractTextShapes(doc);
    
    // Speaker notes are usually in content shapes, not title shapes
    const contentShapes = textShapes.filter(shape => shape.type !== 'title');
    
    return this.formatTextShapeContent(...contentShapes);
  }
  
  private formatTextShapeContent(...shapes: (TextShape | undefined)[]): string {
    const lines: string[] = [];
    
    for (const shape of shapes) {
      if (!shape) continue;
      
      const shapeText = this.formatParagraphs(shape.paragraphs);
      if (shapeText) {
        lines.push(shapeText);
      }
    }
    
    return lines.join('\n\n').trim();
  }
  
  private formatParagraphs(paragraphs: ParsedParagraph[]): string {
    const lines: string[] = [];
    let currentNumbering = new Map<number, number>();
    
    for (const paragraph of paragraphs) {
      const text = paragraph.runs.map(run => run.text).join('');
      
      if (!text.trim()) {
        lines.push(''); // Preserve empty lines
        continue;
      }
      
      const indent = '  '.repeat(paragraph.indentLevel);
      let prefix = '';
      
      switch (paragraph.bulletType) {
        case 'bullet':
          prefix = '• ';
          break;
        case 'custom':
          prefix = `${paragraph.bulletChar || '•'} `;
          break;
        case 'number':
          const currentNum = currentNumbering.get(paragraph.indentLevel) || paragraph.bulletNumber || 1;
          prefix = `${currentNum}. `;
          currentNumbering.set(paragraph.indentLevel, currentNum + 1);
          // Reset deeper levels
          currentNumbering.forEach((value, level) => {
            if (level > paragraph.indentLevel) {
              currentNumbering.delete(level);
            }
          });
          break;
        case 'none':
        default:
          // No bullet prefix
          break;
      }
      
      lines.push(`${indent}${prefix}${text}`);
    }
    
    return lines.join('\n');
  }
  
  private assembleSlideContent(contentShapes: TextShape[], tableContent: string, chartContent: string): string {
    const sections: string[] = [];
    
    // Add regular content shapes
    const regularContent = this.formatTextShapeContent(...contentShapes);
    if (regularContent) {
      sections.push(regularContent);
    }
    
    // Add table content
    if (tableContent) {
      sections.push(tableContent);
    }
    
    // Add chart content
    if (chartContent) {
      sections.push(chartContent);
    }
    
    return sections.join('\n\n').trim();
  }
  
  private extractTextFromElement(element: Element): string {
    const textElements = element.querySelectorAll('a\\:t, t');
    const texts: string[] = [];
    
    for (let i = 0; i < textElements.length; i++) {
      const el = textElements[i];
      const text = el.textContent || '';
      if (text.trim()) {
        texts.push(text);
      }
    }
    
    return texts.join('').trim();
  }
}

// Enhanced version of the original function that uses the new parser
export async function readPPTXFileAdvanced(file: File): Promise<SlideContent[]> {
  const parser = new AdvancedPptParser();
  return await parser.parseFile(file);
} 