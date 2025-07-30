import JSZip from 'jszip';

export interface XMLAnalysisResult {
  slideNumber: number;
  rawXML: string;
  xmlStructure: XMLNodeAnalysis;
  extractedElements: ExtractedElements;
  textAssembly: TextAssemblyInfo;
}

export interface XMLNodeAnalysis {
  totalElements: number;
  textElements: number;
  shapeElements: number;
  paragraphElements: number;
  runElements: number;
  placeholderTypes: string[];
  bulletElements: number;
  tableElements: number;
  chartElements: number;
}

export interface ExtractedElements {
  shapes: {
    name: string;
    type: string;
    placeholder?: string;
    textContent: string;
    bulletInfo?: string;
    position?: string;
  }[];
  tables: {
    rowCount: number;
    columnCount: number;
    cellContents: string[][];
  }[];
  charts: {
    title?: string;
    type?: string;
  }[];
  media: {
    type: string;
    name?: string;
    altText?: string;
  }[];
}

export interface TextAssemblyInfo {
  originalTextRuns: string[];
  assembledParagraphs: string[];
  formattingPreserved: boolean;
  bulletStructureDetected: boolean;
  indentationLevels: number[];
}

export class PPTXmlAnalyzer {
  
  async analyzeFile(file: File): Promise<XMLAnalysisResult[]> {
    const zip = new JSZip();
    const contents = await zip.loadAsync(file);
    
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
    
    const results: XMLAnalysisResult[] = [];
    
    for (const slideFile of slideFiles) {
      const slideContent = await contents.files[slideFile].async('text');
      const slideNumber = parseInt(slideFile.match(/slide(\d+)\.xml/)?.[1] || '0');
      
      const analysis = this.analyzeSlideXML(slideContent, slideNumber);
      results.push(analysis);
    }
    
    return results;
  }
  
  private analyzeSlideXML(xml: string, slideNumber: number): XMLAnalysisResult {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xml, 'text/xml');
    
    const xmlStructure = this.analyzeXMLStructure(doc);
    const extractedElements = this.extractAllElements(doc);
    const textAssembly = this.analyzeTextAssembly(doc);
    
    return {
      slideNumber,
      rawXML: xml,
      xmlStructure,
      extractedElements,
      textAssembly
    };
  }
  
  private analyzeXMLStructure(doc: Document): XMLNodeAnalysis {
    const allElements = doc.querySelectorAll('*');
    const textElements = doc.querySelectorAll('a\\:t, t');
    const shapeElements = doc.querySelectorAll('p\\:sp, sp');
    const paragraphElements = doc.querySelectorAll('a\\:p, p');
    const runElements = doc.querySelectorAll('a\\:r, r');
    const bulletElements = doc.querySelectorAll('a\\:buChar, buChar, a\\:buAutoNum, buAutoNum, a\\:buFont, buFont');
    const tableElements = doc.querySelectorAll('a\\:tbl, tbl');
    const chartElements = doc.querySelectorAll('c\\:chart, chart');
    
    // Analyze placeholder types
    const placeholderTypes: string[] = [];
    const placeholders = doc.querySelectorAll('p\\:ph, ph');
    for (let i = 0; i < placeholders.length; i++) {
      const type = placeholders[i].getAttribute('type');
      if (type && !placeholderTypes.includes(type)) {
        placeholderTypes.push(type);
      }
    }
    
    return {
      totalElements: allElements.length,
      textElements: textElements.length,
      shapeElements: shapeElements.length,
      paragraphElements: paragraphElements.length,
      runElements: runElements.length,
      placeholderTypes,
      bulletElements: bulletElements.length,
      tableElements: tableElements.length,
      chartElements: chartElements.length
    };
  }
  
  private extractAllElements(doc: Document): ExtractedElements {
    const shapes = this.extractShapeDetails(doc);
    const tables = this.extractTableDetails(doc);
    const charts = this.extractChartDetails(doc);
    const media = this.extractMediaDetails(doc);
    
    return { shapes, tables, charts, media };
  }
  
  private extractShapeDetails(doc: Document): ExtractedElements['shapes'] {
    const shapes: ExtractedElements['shapes'] = [];
    const shapeElements = doc.querySelectorAll('p\\:sp, sp');
    
    for (let i = 0; i < shapeElements.length; i++) {
      const shape = shapeElements[i];
      
      // Get shape name and type
      const cNvPr = shape.querySelector('p\\:cNvPr, cNvPr');
      const name = cNvPr?.getAttribute('name') || `Shape ${i + 1}`;
      
      const nvPr = shape.querySelector('p\\:nvPr, nvPr');
      const ph = nvPr?.querySelector('p\\:ph, ph');
      const placeholder = ph?.getAttribute('type') || undefined;
      
      // Determine shape type
      let type = 'content';
      if (name.toLowerCase().includes('title') || placeholder === 'title') {
        type = 'title';
      } else if (placeholder === 'body') {
        type = 'body';
      } else if (shape.querySelector('a\\:tbl, tbl')) {
        type = 'table';
      }
      
      // Extract text content
      const textElements = shape.querySelectorAll('a\\:t, t');
      const textContent = Array.from(textElements)
        .map(el => el.textContent || '')
        .join(' ')
        .trim();
      
      // Analyze bullet info
      let bulletInfo;
      const buChar = shape.querySelector('a\\:buChar, buChar');
      const buAutoNum = shape.querySelector('a\\:buAutoNum, buAutoNum');
      if (buChar) {
        bulletInfo = `Custom bullet: ${buChar.getAttribute('char')}`;
      } else if (buAutoNum) {
        bulletInfo = `Numbered list starting at ${buAutoNum.getAttribute('startAt') || '1'}`;
      } else if (shape.querySelector('a\\:buFont, buFont')) {
        bulletInfo = 'Default bullets';
      }
      
      // Get position info
      let position;
      const xfrm = shape.querySelector('a\\:xfrm, xfrm');
      if (xfrm) {
        const off = xfrm.querySelector('a\\:off, off');
        const ext = xfrm.querySelector('a\\:ext, ext');
        if (off && ext) {
          const x = parseInt(off.getAttribute('x') || '0');
          const y = parseInt(off.getAttribute('y') || '0');
          const w = parseInt(ext.getAttribute('cx') || '0');
          const h = parseInt(ext.getAttribute('cy') || '0');
          position = `x:${Math.round(x/914400)}in, y:${Math.round(y/914400)}in, w:${Math.round(w/914400)}in, h:${Math.round(h/914400)}in`;
        }
      }
      
      if (textContent) {
        shapes.push({
          name,
          type,
          placeholder,
          textContent,
          bulletInfo,
          position
        });
      }
    }
    
    return shapes;
  }
  
  private extractTableDetails(doc: Document): ExtractedElements['tables'] {
    const tables: ExtractedElements['tables'] = [];
    const tableElements = doc.querySelectorAll('a\\:tbl, tbl');
    
    for (let i = 0; i < tableElements.length; i++) {
      const table = tableElements[i];
      const rows = table.querySelectorAll('a\\:tr, tr');
      const cellContents: string[][] = [];
      let maxColumns = 0;
      
      for (let j = 0; j < rows.length; j++) {
        const row = rows[j];
        const cells = row.querySelectorAll('a\\:tc, tc');
        const rowContents: string[] = [];
        
        for (let k = 0; k < cells.length; k++) {
          const cell = cells[k];
          const textElements = cell.querySelectorAll('a\\:t, t');
          const cellText = Array.from(textElements)
            .map(el => el.textContent || '')
            .join(' ')
            .trim();
          rowContents.push(cellText);
        }
        
        cellContents.push(rowContents);
        maxColumns = Math.max(maxColumns, rowContents.length);
      }
      
      tables.push({
        rowCount: rows.length,
        columnCount: maxColumns,
        cellContents
      });
    }
    
    return tables;
  }
  
  private extractChartDetails(doc: Document): ExtractedElements['charts'] {
    const charts: ExtractedElements['charts'] = [];
    const chartElements = doc.querySelectorAll('c\\:chart, chart');
    
    for (let i = 0; i < chartElements.length; i++) {
      const chart = chartElements[i];
      const title = chart.querySelector('c\\:title, title');
      const titleText = title ? 
        Array.from(title.querySelectorAll('a\\:t, t'))
          .map(el => el.textContent || '')
          .join(' ')
          .trim() : undefined;
      
      charts.push({
        title: titleText,
        type: 'chart' // Could be enhanced to detect specific chart types
      });
    }
    
    return charts;
  }
  
  private extractMediaDetails(doc: Document): ExtractedElements['media'] {
    const media: ExtractedElements['media'] = [];
    
    // Look for images
    const picElements = doc.querySelectorAll('pic\\:pic, pic');
    for (let i = 0; i < picElements.length; i++) {
      const pic = picElements[i];
      const cNvPr = pic.querySelector('pic\\:cNvPr, cNvPr');
      
      media.push({
        type: 'image',
        name: cNvPr?.getAttribute('name') || undefined,
        altText: cNvPr?.getAttribute('descr') || undefined
      });
    }
    
    // Look for videos/audio
    const mediaElements = doc.querySelectorAll('[r\\:id*="media"], [r\\:embed]');
    for (let i = 0; i < mediaElements.length; i++) {
      const mediaEl = mediaElements[i];
      media.push({
        type: 'media',
        name: mediaEl.getAttribute('name') || undefined
      });
    }
    
    return media;
  }
  
  private analyzeTextAssembly(doc: Document): TextAssemblyInfo {
    const originalTextRuns: string[] = [];
    const assembledParagraphs: string[] = [];
    const indentationLevels: number[] = [];
    
    let formattingPreserved = false;
    let bulletStructureDetected = false;
    
    // Analyze text runs
    const runElements = doc.querySelectorAll('a\\:r, r');
    for (let i = 0; i < runElements.length; i++) {
      const run = runElements[i];
      const textEl = run.querySelector('a\\:t, t');
      if (textEl && textEl.textContent) {
        originalTextRuns.push(textEl.textContent);
        
        // Check for formatting
        const rPr = run.querySelector('a\\:rPr, rPr');
        if (rPr && (rPr.getAttribute('b') === '1' || rPr.getAttribute('i') === '1')) {
          formattingPreserved = true;
        }
      }
    }
    
    // Analyze paragraphs and bullets
    const paragraphElements = doc.querySelectorAll('a\\:p, p');
    for (let i = 0; i < paragraphElements.length; i++) {
      const paragraph = paragraphElements[i];
      const textElements = paragraph.querySelectorAll('a\\:t, t');
      const paragraphText = Array.from(textElements)
        .map(el => el.textContent || '')
        .join('')
        .trim();
      
      if (paragraphText) {
        assembledParagraphs.push(paragraphText);
        
        // Check for bullets
        const pPr = paragraph.querySelector('a\\:pPr, pPr');
        if (pPr) {
          if (pPr.querySelector('a\\:buChar, buChar, a\\:buAutoNum, buAutoNum, a\\:buFont, buFont')) {
            bulletStructureDetected = true;
          }
          
          // Check indentation
          const marL = pPr.getAttribute('marL');
          if (marL) {
            const level = Math.floor(parseInt(marL) / 457200);
            if (!indentationLevels.includes(level)) {
              indentationLevels.push(level);
            }
          }
        }
      }
    }
    
    indentationLevels.sort();
    
    return {
      originalTextRuns,
      assembledParagraphs,
      formattingPreserved,
      bulletStructureDetected,
      indentationLevels
    };
  }
  
  // Utility method to generate a readable analysis report
  generateAnalysisReport(analysis: XMLAnalysisResult): string {
    const report: string[] = [];
    
    report.push(`=== PowerPoint XML Analysis - Slide ${analysis.slideNumber} ===\n`);
    
    report.push(`XML Structure:`);
    report.push(`- Total XML elements: ${analysis.xmlStructure.totalElements}`);
    report.push(`- Text elements (a:t): ${analysis.xmlStructure.textElements}`);
    report.push(`- Shape elements (p:sp): ${analysis.xmlStructure.shapeElements}`);
    report.push(`- Paragraph elements (a:p): ${analysis.xmlStructure.paragraphElements}`);
    report.push(`- Text run elements (a:r): ${analysis.xmlStructure.runElements}`);
    report.push(`- Bullet elements: ${analysis.xmlStructure.bulletElements}`);
    report.push(`- Table elements: ${analysis.xmlStructure.tableElements}`);
    report.push(`- Chart elements: ${analysis.xmlStructure.chartElements}`);
    report.push(`- Placeholder types: ${analysis.xmlStructure.placeholderTypes.join(', ') || 'None'}\n`);
    
    report.push(`Extracted Content:`);
    report.push(`- ${analysis.extractedElements.shapes.length} text shapes found`);
    analysis.extractedElements.shapes.forEach((shape, i) => {
      report.push(`  Shape ${i + 1}: ${shape.name} (${shape.type})`);
      if (shape.placeholder) report.push(`    Placeholder: ${shape.placeholder}`);
      if (shape.position) report.push(`    Position: ${shape.position}`);
      if (shape.bulletInfo) report.push(`    Bullets: ${shape.bulletInfo}`);
      report.push(`    Text: "${shape.textContent.substring(0, 100)}${shape.textContent.length > 100 ? '...' : ''}"`);
    });
    
    if (analysis.extractedElements.tables.length > 0) {
      report.push(`\n- ${analysis.extractedElements.tables.length} table(s) found`);
      analysis.extractedElements.tables.forEach((table, i) => {
        report.push(`  Table ${i + 1}: ${table.rowCount} rows × ${table.columnCount} columns`);
      });
    }
    
    if (analysis.extractedElements.charts.length > 0) {
      report.push(`\n- ${analysis.extractedElements.charts.length} chart(s) found`);
      analysis.extractedElements.charts.forEach((chart, i) => {
        report.push(`  Chart ${i + 1}: ${chart.title || 'Untitled'}`);
      });
    }
    
    if (analysis.extractedElements.media.length > 0) {
      report.push(`\n- ${analysis.extractedElements.media.length} media element(s) found`);
      analysis.extractedElements.media.forEach((media, i) => {
        report.push(`  Media ${i + 1}: ${media.type} - ${media.name || 'Unnamed'}${media.altText ? ` (Alt: ${media.altText})` : ''}`);
      });
    }
    
    report.push(`\nText Assembly Analysis:`);
    report.push(`- Original text runs: ${analysis.textAssembly.originalTextRuns.length}`);
    report.push(`- Assembled paragraphs: ${analysis.textAssembly.assembledParagraphs.length}`);
    report.push(`- Formatting preserved: ${analysis.textAssembly.formattingPreserved ? 'Yes' : 'No'}`);
    report.push(`- Bullet structure detected: ${analysis.textAssembly.bulletStructureDetected ? 'Yes' : 'No'}`);
    report.push(`- Indentation levels used: ${analysis.textAssembly.indentationLevels.join(', ') || 'None'}`);
    
    return report.join('\n');
  }
}

// Helper function to compare basic vs advanced parsing
export async function compareParseMethods(file: File): Promise<{
  basic: any;
  advanced: any;
  analysis: XMLAnalysisResult[];
}> {
  // Import the parsers
  const { readPPTXFile } = await import('./pptReader');
  const { readPPTXFileAdvanced } = await import('./advancedPptParser');
  
  const analyzer = new PPTXmlAnalyzer();
  
  const [basic, advanced, analysis] = await Promise.all([
    readPPTXFile(file),
    readPPTXFileAdvanced(file),
    analyzer.analyzeFile(file)
  ]);
  
  return { basic, advanced, analysis };
} 