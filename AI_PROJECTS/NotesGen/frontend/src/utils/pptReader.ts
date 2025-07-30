import JSZip from 'jszip';
import { SlideContent } from '../types/ppt';

export async function readPPTXFile(file: File): Promise<SlideContent[]> {
  const zip = new JSZip();
  const contents = await zip.loadAsync(file);
  const slides: SlideContent[] = [];
  
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
  
  // Read each slide
  for (const slideFile of slideFiles) {
    const slideContent = await contents.files[slideFile].async('text');
    const slideNumber = parseInt(slideFile.match(/slide(\d+)\.xml/)?.[1] || '0');
    
    // Extract different types of content
    const title = extractTitleFromSlideXML(slideContent);
    const content = extractContentFromSlideXML(slideContent);
    const altText = extractAltTextFromSlideXML(slideContent);
    
    // Try to get speaker notes
    const notesFile = `ppt/notesSlides/notesSlide${slideNumber}.xml`;
    let speakerNotes = '';
    if (contents.files[notesFile]) {
      const notesContent = await contents.files[notesFile].async('text');
      speakerNotes = extractSpeakerNotesFromXML(notesContent);
    }
    
    slides.push({
      slideNumber,
      title,
      content,
      altText,
      speakerNotes
    });
  }
  
  return slides;
}

function extractTitleFromSlideXML(xml: string): string {
  // Look for title placeholders first
  const titlePlaceholderRegex = /<p:sp[^>]*>\s*<p:nvSpPr>\s*<p:cNvPr[^>]*name="Title[^"]*"[^>]*>/;
  const titleMatch = xml.match(titlePlaceholderRegex);
  
  if (titleMatch) {
    // Find the text content within this title shape
    const titleIndex = xml.indexOf(titleMatch[0]);
    const titleEnd = xml.indexOf('</p:sp>', titleIndex);
    const titleSection = xml.substring(titleIndex, titleEnd);
    
    const textMatches = titleSection.match(/<a:t>([^<]*)<\/a:t>/g) || [];
    if (textMatches.length > 0) {
      return textMatches.map(match => 
        match.replace(/<a:t>/, '').replace(/<\/a:t>/, '')
      ).join(' ').trim();
    }
  }
  
  // Fallback: try to find first text content as title
  const allTextMatches = xml.match(/<a:t>([^<]*)<\/a:t>/g) || [];
  if (allTextMatches.length > 0 && allTextMatches[0]) {
    return allTextMatches[0].replace(/<a:t>/, '').replace(/<\/a:t>/, '').trim();
  }
  
  return 'Untitled';
}

function extractContentFromSlideXML(xml: string): string {
  // Extract formatted content preserving exact structure
  const formattedText: string[] = [];
  
  // Look for text shapes that are not titles
  const shapeMatches = xml.match(/<p:sp[^>]*>[\s\S]*?<\/p:sp>/g) || [];
  
  for (const shape of shapeMatches) {
    // Skip title shapes
    if (shape.includes('name="Title') || shape.includes('type="title"')) {
      continue;
    }
    
    // Look for paragraph elements in this shape
    const paragraphMatches = shape.match(/<a:p[^>]*>[\s\S]*?<\/a:p>/g) || [];
    
    for (const paragraph of paragraphMatches) {
      // Extract text content from this paragraph
      const textMatches = paragraph.match(/<a:t>([^<]*)<\/a:t>/g) || [];
      const paragraphText = textMatches.map(match => 
        match.replace(/<a:t>/, '').replace(/<\/a:t>/, '')
      ).join('').trim();
      
      if (paragraphText) {
        // Check for different bullet types in PowerPoint
        let bulletChar = '';
        let hasCustomBullet = false;
        
        // Look for custom bullet character
        const bulletCharMatch = paragraph.match(/<a:buChar[^>]*char="([^"]*)"/);
        if (bulletCharMatch) {
          bulletChar = bulletCharMatch[1];
          hasCustomBullet = true;
        }
        
        // Check for numbered bullets
        const numberedBullet = paragraph.includes('<a:buAutoNum');
        
        // Check for default bullets
        const hasDefaultBullet = paragraph.includes('<a:buFont') || paragraph.includes('<a:buSzPct');
        
        // Check for indentation level
        const leftMarginMatch = paragraph.match(/<a:pPr[^>]*marL="([^"]*)"/);
        let indentLevel = 0;
        let actualIndent = '';
        
        if (leftMarginMatch) {
          const marginValue = parseInt(leftMarginMatch[1]) || 0;
          indentLevel = Math.floor(marginValue / 457200);
          
          if (indentLevel > 0) {
            actualIndent = '  '.repeat(indentLevel);
          }
        }
        
        // Build the formatted line based on detected formatting
        let formattedLine = '';
        
        if (hasCustomBullet && bulletChar) {
          // Use the actual bullet character from PowerPoint
          formattedLine = `${actualIndent}${bulletChar} ${paragraphText}`;
        } else if (numberedBullet) {
          // For numbered bullets
          formattedLine = `${actualIndent}• ${paragraphText}`;
        } else if (hasDefaultBullet) {
          // Default bullet point
          formattedLine = `${actualIndent}• ${paragraphText}`;
        } else {
          // No bullet, just text with potential indentation
          formattedLine = `${actualIndent}${paragraphText}`;
        }
        
        formattedText.push(formattedLine);
      } else {
        // Empty paragraph - preserve as line break for spacing
        formattedText.push('');
      }
    }
  }
  
  // If no formatted content found, fall back to simple extraction
  if (formattedText.length === 0) {
    const textMatches = xml.match(/<a:t>([^<]*)<\/a:t>/g) || [];
    const texts = textMatches.map(match => 
      match.replace(/<a:t>/, '').replace(/<\/a:t>/, '').trim()
    ).filter(text => text.length > 0);
    
    // Remove first text if it looks like a title
    if (texts.length > 1) {
      texts.shift();
    }
    
    return texts.join('\n• ').trim();
  }
  
  // Join with newlines and clean up excessive empty lines
  let result = formattedText.join('\n');
  
  // Clean up multiple consecutive empty lines but preserve intentional spacing
  result = result.replace(/\n\n\n+/g, '\n\n');
  
  return result.trim();
}

function extractAltTextFromSlideXML(xml: string): string[] {
  const altTextArray: string[] = [];
  
  // Look for alt text in image descriptions
  const altTextMatches = xml.match(/descr="([^"]*)"/g) || [];
  altTextMatches.forEach(match => {
    const altText = match.replace(/descr="/, '').replace(/"$/, '').trim();
    if (altText && altText !== '') {
      altTextArray.push(altText);
    }
  });
  
  // Also look for title attributes
  const titleMatches = xml.match(/title="([^"]*)"/g) || [];
  titleMatches.forEach(match => {
    const titleText = match.replace(/title="/, '').replace(/"$/, '').trim();
    if (titleText && titleText !== '' && !altTextArray.includes(titleText)) {
      altTextArray.push(titleText);
    }
  });
  
  return altTextArray;
}

function extractSpeakerNotesFromXML(xml: string): string {
  // Enhanced speaker notes extraction with proper structure parsing
  const formattedSections: string[] = [];
  
  console.log('🔍 Speaker Notes XML:', xml.substring(0, 500) + '...');
  
  // Look for paragraph elements in the notes
  const paragraphMatches = xml.match(/<a:p[^>]*>[\s\S]*?<\/a:p>/g) || [];
  
  console.log('📝 Found paragraphs:', paragraphMatches.length);
  
  let currentSection = '';
  let currentSectionContent: string[] = [];
  
  for (const paragraph of paragraphMatches) {
    // Extract text content from this paragraph
    const textMatches = paragraph.match(/<a:t>([^<]*)<\/a:t>/g) || [];
    const paragraphText = textMatches.map(match => 
      match.replace(/<a:t>/, '').replace(/<\/a:t>/, '')
    ).join('').trim();
    
    if (paragraphText) {
      // Check if this is a section header  
      const cleanText = paragraphText.replace(/^[|~•◦▪▫]+\s*/, '');
      const upperText = cleanText.toUpperCase();
      
      let isNewSection = false;
      let newSectionType = '';
      
      // Detect section headers
      if (upperText.includes('INSTRUCTOR NOTES') || upperText.includes('TEACHER NOTES')) {
        isNewSection = true;
        newSectionType = 'INSTRUCTOR NOTES';
      } else if (upperText.includes('STUDENT NOTES') || upperText.includes('LEARNER NOTES')) {
        isNewSection = true;
        newSectionType = 'STUDENT NOTES';
      } else if (upperText.includes('DEVELOPER NOTES') || upperText.includes('DEV NOTES')) {
        isNewSection = true;
        newSectionType = 'DEVELOPER NOTES';
      } else if (upperText.includes('ALT TEXT') || upperText.includes('IMAGE DESCRIPTION')) {
        isNewSection = true;
        newSectionType = 'ALT TEXT';
      }
      
      if (isNewSection) {
        // Save previous section
        if (currentSection && currentSectionContent.length > 0) {
          formattedSections.push(formatSection(currentSection, currentSectionContent));
        }
        
        // Start new section
        currentSection = newSectionType;
        currentSectionContent = [];
      } else {
        // Process paragraph formatting
        const formattedParagraph = formatParagraphText(paragraph, paragraphText);
        if (formattedParagraph) {
          currentSectionContent.push(formattedParagraph);
        }
      }
    }
  }
  
  // Add final section
  if (currentSection && currentSectionContent.length > 0) {
    formattedSections.push(formatSection(currentSection, currentSectionContent));
  } else if (currentSectionContent.length > 0) {
    // No section headers found, treat as general notes
    formattedSections.push(formatSection('NOTES', currentSectionContent));
  }
  
  // If no structured content found, fall back to simple extraction
  if (formattedSections.length === 0) {
    const textMatches = xml.match(/<a:t>([^<]*)<\/a:t>/g) || [];
    const texts = textMatches.map(match => 
      match.replace(/<a:t>/, '').replace(/<\/a:t>/, '').trim()
    ).filter(text => text.length > 0);
    
    return texts.join(' ').trim();
  }
  
  return formattedSections.join('\n').trim();
}

function formatParagraphText(paragraphXml: string, text: string): string {
  // Clean up structure characters while preserving meaningful content
  let cleanText = text.replace(/^[|~•◦▪▫-]+\s*/, '');
  
  // Remove patterns like "- |" that are structural artifacts
  cleanText = cleanText.replace(/\s*-\s*\|\s*/g, ' ');
  
  // Handle special cases where || separates content
  if (cleanText.includes('||')) {
    const parts = cleanText.split('||');
    cleanText = parts.map(part => part.trim()).filter(part => part).join('\n');
  }
  
  if (!cleanText.trim()) {
    return '';
  }
  
  // Check for bullet formatting
  let bulletChar = '';
  let hasCustomBullet = false;
  
  // Look for custom bullet character
  const bulletCharMatch = paragraphXml.match(/<a:buChar[^>]*char="([^"]*)"/);
  if (bulletCharMatch) {
    bulletChar = bulletCharMatch[1];
    hasCustomBullet = true;
  }
  
  // Check for numbered bullets
  const numberedBullet = paragraphXml.includes('<a:buAutoNum');
  
  // Check for default bullets
  const hasDefaultBullet = paragraphXml.includes('<a:buFont') || paragraphXml.includes('<a:buSzPct');
  
  // Check for indentation level
  const leftMarginMatch = paragraphXml.match(/<a:pPr[^>]*marL="([^"]*)"/);
  let indentLevel = 0;
  
  if (leftMarginMatch) {
    const marginValue = parseInt(leftMarginMatch[1]) || 0;
    indentLevel = Math.floor(marginValue / 457200);
  }
  
  // Build formatted text - remove indentation and increase spacing after bullet
  let bulletPrefix = '';
  
  if (hasCustomBullet && bulletChar) {
    // Custom bullet with 5 spaces after it (no indent)
    bulletPrefix = `${bulletChar}     `;
  } else if (numberedBullet) {
    // Numbered bullet with 5 spaces after it (no indent)
    bulletPrefix = '•     ';
  } else if (hasDefaultBullet) {
    // Default bullet with 5 spaces after it (no indent)
    bulletPrefix = '•     ';
  }
  
  // Return with no indent before bullet, just bullet + spacing + text
  return `${bulletPrefix}${cleanText}`;
}

function formatSection(sectionType: string, content: string[]): string {
  // Use special characters from PowerPoint matching screenshot format
  const sectionHeaders: { [key: string]: string } = {
    'INSTRUCTOR NOTES': '|INSTRUCTOR NOTES:',
    'STUDENT NOTES': '|STUDENT NOTES:',
    'DEVELOPER NOTES': '~Developer Notes:',
    'ALT TEXT': '~Alt text:',
  };
  
  const header = sectionHeaders[sectionType] || `\n${sectionType}:`;
  
  if (sectionType === 'INSTRUCTOR NOTES') {
    // Format instructor notes: align left with proper spacing after bullet
    const formattedContent = content.map(line => {
      const trimmed = line.trim();
      if (!trimmed) return '';
      
      // Remove any existing bullets, indentation, or | characters first, but preserve content
      const cleanLine = trimmed.replace(/^[\s•|-]+\s*/, '');
      
      // Format as: | + 3 spaces + text (align left, little space before text)
      return `|   ${cleanLine}`;
    }).filter(line => line);
    
    // Add empty line with | for spacing
    formattedContent.push('|');
    
    return `${header}\n${formattedContent.join('\n')}`;
  } else if (sectionType === 'STUDENT NOTES') {
    // Format student notes as readable paragraphs with NO prefixes (plain text)
    let paragraphText = content.join(' ').replace(/\s+/g, ' ').trim();
    
    // Remove any bullet characters from student notes (make completely plain text)
    paragraphText = paragraphText.replace(/^[•*-]+\s*/g, '').replace(/\s[•*-]+\s/g, ' ');
    
    return `${header}\n${paragraphText}`;
  } else if (sectionType === 'DEVELOPER NOTES') {
    // Format developer notes with ~ prefix matching PowerPoint format
    const formattedContent = content.map(line => {
      const trimmed = line.trim();
      if (!trimmed) return '';
      
      // Ensure ~ prefix for all developer notes lines
      if (!trimmed.startsWith('~')) {
        return `~${trimmed}`;
      }
      return trimmed;
    }).filter(line => line);
    
    // Add empty line with ~ for spacing
    formattedContent.push('~');
    
    return `${header}\n${formattedContent.join('\n')}`;
  } else if (sectionType === 'ALT TEXT') {
    // Format alt text with tilde prefix matching screenshots
    const formattedContent = content.map(line => {
      const trimmed = line.trim();
      if (trimmed) {
        if (trimmed.toLowerCase().includes('no images') || trimmed.toLowerCase().includes('no image')) {
          return `~${trimmed}`;
        } else if (trimmed.startsWith('~')) {
          return trimmed; // Already has tilde
        } else {
          return `~${trimmed}`;
        }
      }
      return trimmed;
    }).filter(line => line);
    
    // Add empty line with ~ for spacing
    formattedContent.push('~');
    
    return formattedContent.length > 0 ? `${header}\n${formattedContent.join('\n')}` : '';
  } else {
    // General formatting
    return `${header}\n${content.join('\n')}`;
  }
} 