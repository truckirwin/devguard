import JSZip from 'jszip';
import { TextShape, ParsedParagraph, TextRun } from './advancedPptParser';

export interface SlidePreview {
  slideNumber: number;
  imageUrl?: string; // Base64 data URL for extracted image
  htmlPreview?: string; // HTML representation as fallback
  width: number;
  height: number;
  hasImage: boolean;
}

export class SlideImageExtractor {
  private zip: JSZip | null = null;
  
  async extractSlidePreviews(file: File, textShapes: TextShape[][]): Promise<SlidePreview[]> {
    this.zip = new JSZip();
    const contents = await this.zip.loadAsync(file);
    
    const previews: SlidePreview[] = [];
    
    // First, try to extract existing slide thumbnails
    const thumbnails = await this.extractSlideThumbnails(contents);
    
    // Get slide count
    const slideFiles = Object.keys(contents.files).filter(name => 
      name.startsWith('ppt/slides/slide') && name.endsWith('.xml')
    );
    
    for (let i = 0; i < slideFiles.length; i++) {
      const slideNumber = i + 1;
      const thumbnail = thumbnails.get(slideNumber);
      
      if (thumbnail) {
        // We have an actual image thumbnail
        previews.push({
          slideNumber,
          imageUrl: thumbnail.dataUrl,
          width: thumbnail.width || 1920,
          height: thumbnail.height || 1080,
          hasImage: true
        });
      } else {
        // Generate HTML preview from text shapes
        const shapes = textShapes[i] || [];
        const htmlPreview = this.generateHTMLPreview(shapes, slideNumber);
        
        previews.push({
          slideNumber,
          htmlPreview,
          width: 1920,
          height: 1080,
          hasImage: false
        });
      }
    }
    
    return previews;
  }
  
  private async extractSlideThumbnails(contents: JSZip): Promise<Map<number, { dataUrl: string; width?: number; height?: number }>> {
    const thumbnails = new Map<number, { dataUrl: string; width?: number; height?: number }>();
    
    // Look for thumbnails in various locations
    const possibleThumbnailPaths = [
      'docProps/thumbnail.jpeg',
      'docProps/thumbnail.png',
      'ppt/media/',
      'ppt/slides/_rels/',
      'ppt/slideMasters/_rels/',
      'ppt/prsThumbnail.jpeg'
    ];
    
    // Check for presentation thumbnail first
    for (const path of possibleThumbnailPaths) {
      if (path.endsWith('/')) {
        // Check directory for slide-specific thumbnails
        await this.extractFromDirectory(contents, path, thumbnails);
      } else {
        // Check specific file
        if (contents.files[path]) {
          try {
            const imageData = await contents.files[path].async('base64');
            const mimeType = path.endsWith('.png') ? 'image/png' : 'image/jpeg';
            const dataUrl = `data:${mimeType};base64,${imageData}`;
            
            // This is usually the presentation thumbnail, use for slide 1
            thumbnails.set(1, { dataUrl });
          } catch (error) {
            console.warn(`Failed to extract thumbnail from ${path}:`, error);
          }
        }
      }
    }
    
    // Look for slide-specific images in media folder
    await this.extractSlideImages(contents, thumbnails);
    
    return thumbnails;
  }
  
  private async extractFromDirectory(contents: JSZip, dirPath: string, thumbnails: Map<number, { dataUrl: string; width?: number; height?: number }>) {
    const files = Object.keys(contents.files).filter(name => name.startsWith(dirPath));
    
    for (const filePath of files) {
      if (filePath.match(/\.(jpe?g|png|gif|bmp)$/i)) {
        try {
          const slideMatch = filePath.match(/slide(\d+)/i);
          const slideNumber = slideMatch ? parseInt(slideMatch[1]) : 1;
          
          const imageData = await contents.files[filePath].async('base64');
          const extension = filePath.split('.').pop()?.toLowerCase();
          const mimeType = extension === 'png' ? 'image/png' : 
                          extension === 'gif' ? 'image/gif' :
                          extension === 'bmp' ? 'image/bmp' : 'image/jpeg';
          
          const dataUrl = `data:${mimeType};base64,${imageData}`;
          
          if (!thumbnails.has(slideNumber)) {
            thumbnails.set(slideNumber, { dataUrl });
          }
        } catch (error) {
          console.warn(`Failed to extract image from ${filePath}:`, error);
        }
      }
    }
  }
  
  private async extractSlideImages(contents: JSZip, thumbnails: Map<number, { dataUrl: string; width?: number; height?: number }>) {
    // Look for images in the media folder that might be slide backgrounds or content
    const mediaFiles = Object.keys(contents.files).filter(name => 
      name.startsWith('ppt/media/') && name.match(/\.(jpe?g|png|gif|bmp)$/i)
    );
    
    for (const mediaFile of mediaFiles) {
      try {
        // Try to find which slide this image belongs to by checking relationships
        const imageData = await contents.files[mediaFile].async('base64');
        const extension = mediaFile.split('.').pop()?.toLowerCase();
        const mimeType = extension === 'png' ? 'image/png' : 
                        extension === 'gif' ? 'image/gif' :
                        extension === 'bmp' ? 'image/bmp' : 'image/jpeg';
        
        const dataUrl = `data:${mimeType};base64,${imageData}`;
        
        // For now, assign to slides that don't have thumbnails yet
        for (let i = 1; i <= 10; i++) { // Assume max 10 slides for now
          if (!thumbnails.has(i)) {
            thumbnails.set(i, { dataUrl });
            break;
          }
        }
      } catch (error) {
        console.warn(`Failed to extract media file ${mediaFile}:`, error);
      }
    }
  }
  
  private generateHTMLPreview(shapes: TextShape[], slideNumber: number): string {
    let html = `
      <div style="
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        position: relative;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        padding: 40px;
        box-sizing: border-box;
      ">
    `;
    
    // If no shapes are provided, create a simple placeholder
    if (!shapes || shapes.length === 0) {
      html += `
        <div style="
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          text-align: center;
        ">
          <div style="
            font-size: 64px;
            font-weight: bold;
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 20px;
          ">
            Slide ${slideNumber}
          </div>
          <div style="
            font-size: 24px;
            color: rgba(255,255,255,0.8);
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
          ">
            PowerPoint Content
          </div>
        </div>
      `;
    } else {
      // Sort shapes by type and position
      const titleShapes = shapes.filter(shape => shape.type === 'title');
      const contentShapes = shapes.filter(shape => shape.type !== 'title');
      
      // Add title
      if (titleShapes.length > 0) {
        const titleText = this.formatShapeText(titleShapes[0]);
        html += `
          <div style="
            font-size: 48px;
            font-weight: bold;
            color: white;
            text-align: center;
            margin-bottom: 40px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            line-height: 1.2;
          ">
            ${this.escapeHtml(titleText)}
          </div>
        `;
      }
      
      // Add content shapes
      if (contentShapes.length > 0) {
        html += `<div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">`;
        
        contentShapes.forEach((shape, index) => {
          const formattedContent = this.formatParagraphsAsHTML(shape.paragraphs);
          
          html += `
            <div style="
              background: rgba(255,255,255,0.9);
              padding: 30px;
              border-radius: 15px;
              margin-bottom: 20px;
              box-shadow: 0 8px 32px rgba(0,0,0,0.1);
              backdrop-filter: blur(10px);
              ${index === contentShapes.length - 1 ? 'margin-bottom: 0;' : ''}
            ">
              ${formattedContent}
            </div>
          `;
        });
        
        html += `</div>`;
      }
    }
    
    // Add slide number
    html += `
      <div style="
        position: absolute;
        bottom: 20px;
        right: 20px;
        background: rgba(0,0,0,0.5);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
      ">
        ${slideNumber}
      </div>
    `;
    
    html += `</div>`;
    
    return html;
  }
  
  private formatShapeText(shape: TextShape): string {
    return shape.paragraphs
      .map(paragraph => paragraph.runs.map(run => run.text).join(''))
      .filter(text => text.trim())
      .join('\n');
  }
  
  private formatParagraphsAsHTML(paragraphs: ParsedParagraph[]): string {
    let html = '';
    let currentNumbering = new Map<number, number>();
    
    for (const paragraph of paragraphs) {
      const text = paragraph.runs.map((run: TextRun) => {
        let formattedText = this.escapeHtml(run.text);
        
        if (run.formatting) {
          if (run.formatting.bold) {
            formattedText = `<strong>${formattedText}</strong>`;
          }
          if (run.formatting.italic) {
            formattedText = `<em>${formattedText}</em>`;
          }
          if (run.formatting.underline) {
            formattedText = `<u>${formattedText}</u>`;
          }
          
          let style = '';
          if (run.formatting.fontSize) {
            style += `font-size: ${run.formatting.fontSize}pt; `;
          }
          if (run.formatting.fontFamily) {
            style += `font-family: "${run.formatting.fontFamily}"; `;
          }
          if (run.formatting.color) {
            style += `color: ${run.formatting.color}; `;
          }
          
          if (style) {
            formattedText = `<span style="${style}">${formattedText}</span>`;
          }
        }
        
        return formattedText;
      }).join('');
      
      if (!text.trim()) {
        html += '<br>';
        continue;
      }
      
      const indent = paragraph.indentLevel * 20;
      let prefix = '';
      let listStyle = 'margin-left: ' + indent + 'px; ';
      
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
          currentNumbering.forEach((value: number, level: number) => {
            if (level > paragraph.indentLevel) {
              currentNumbering.delete(level);
            }
          });
          break;
      }
      
      html += `<div style="${listStyle} margin-bottom: 8px; line-height: 1.4;">${prefix}${text}</div>`;
    }
    
    return html || '<div style="color: #666; font-style: italic;">No content</div>';
  }
  
  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Utility function to convert HTML to canvas for image generation
export function htmlToCanvas(html: string, width: number = 1920, height: number = 1080): Promise<string> {
  return new Promise((resolve, reject) => {
    // Create a temporary container
    const container = document.createElement('div');
    container.style.width = width + 'px';
    container.style.height = height + 'px';
    container.style.position = 'absolute';
    container.style.left = '-9999px';
    container.style.top = '-9999px';
    container.innerHTML = html;
    
    document.body.appendChild(container);
    
    // Use html2canvas or similar library if available, otherwise return the HTML
    // For now, we'll return the HTML itself as a data URL
    try {
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      
      if (!ctx) {
        throw new Error('Could not get canvas context');
      }
      
      // Simple text rendering - for production, you'd want to use html2canvas
      ctx.fillStyle = '#667eea';
      ctx.fillRect(0, 0, width, height);
      
      ctx.fillStyle = 'white';
      ctx.font = '48px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('Slide Preview', width / 2, height / 2);
      
      const dataUrl = canvas.toDataURL('image/png');
      
      document.body.removeChild(container);
      resolve(dataUrl);
    } catch (error) {
      document.body.removeChild(container);
      reject(error);
    }
  });
} 