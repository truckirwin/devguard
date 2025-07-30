import { useTheme } from '../contexts/ThemeContext';

export const getThemeColors = (theme: 'light' | 'dark') => {
  return {
    // Background colors - Updated to match black-on-black Cursor theme
    bg: theme === 'light' ? 'white' : '#0a0a0a',
    bgSecondary: theme === 'light' ? '#F7FAFC' : '#111111',
    bgTertiary: theme === 'light' ? '#EDF2F7' : '#1a1a1a',
    headerBg: theme === 'light' ? '#E2E8F0' : '#0f0f0f',
    
    // Text colors - Subtle grays for black-on-black theme
    text: theme === 'light' ? '#1A202C' : '#d4d4d4',
    textSecondary: theme === 'light' ? '#4A5568' : '#a0a0a0',
    textMuted: theme === 'light' ? '#718096' : '#6a6a6a',
    noFolderText: theme === 'light' ? '#8E8E8E' : '#707070',
    pptxText: theme === 'light' ? '#3C3C3C' : '#d4d4d4',
    
    // Border colors - Very subtle borders for minimal contrast
    border: theme === 'light' ? '#E2E8F0' : '#2a2a2a',
    borderLight: theme === 'light' ? '#F7FAFC' : '#1a1a1a',
    
    // Button colors - Minimal contrast
    buttonBg: theme === 'light' ? 'transparent' : 'transparent',
    buttonText: theme === 'light' ? '#1A202C' : '#d4d4d4',
    buttonHover: theme === 'light' ? '#F7FAFC' : '#1a1a1a',
    
    // Input colors - Dark inputs with subtle borders
    inputBg: theme === 'light' ? 'white' : '#1a1a1a',
    inputBorder: theme === 'light' ? '#E2E8F0' : '#333333',
    inputText: theme === 'light' ? '#1A202C' : '#d4d4d4',
    
    // Hover colors - Subtle hover effects
    hoverBg: theme === 'light' ? '#F7FAFC' : '#1a1a1a',
    
    // File/folder icon colors - Slightly muted for dark theme
    blueFolder: '#8a9ba8',
    pptxFile: '#e07b47',
    regularFile: '#707070',
    
    // Badge colors - Adjusted for dark theme visibility
    restoredBadgeColor: theme === 'light' ? '#22C55E' : '#4ade80',
    restoredBadgeBg: theme === 'light' ? '#F0FDF4' : '#1a2e1a',
  };
};

export const useThemeColors = () => {
  const { theme } = useTheme();
  
  if (theme === 'dark') {
    return {
      // Base colors - pure black terminal-like theme
      bg: '#000000',              // Pure black background
      bgSecondary: '#0a0a0a',     // Very dark panels
      bgTertiary: '#111111',      // Slightly lighter surfaces
      
      // Text colors - mostly white
      text: '#ffffff',            // Pure white primary text
      textSecondary: '#cccccc',   // Light gray secondary text
      textMuted: '#888888',       // Medium gray muted text
      
      // Field colors - all white for consistency
      developerNotesColor: '#ffffff',    // White text
      instructorNotesColor: '#ffffff',   // White text
      studentNotesColor: '#ffffff',      // White text
      referencesColor: '#ffffff',        // White text
      scriptColor: '#ffffff',            // White text
      altTextColor: '#ffffff',           // White text
      
      // UI element colors
      border: '#333333',          // Dark gray borders
      inputBg: '#000000',         // Black input backgrounds
      inputBorder: '#333333',     // Dark gray input borders
      inputText: '#ffffff',       // White input text
      
      // Interactive elements
      buttonText: '#ffffff',
      buttonHover: '#111111',
      
      // Accent colors
      titleAccent: '#ffffff',
      bulletAccent: '#ffffff',
      urlAccent: '#ffffff',
      codeAccent: '#ffffff',
      
      // Legacy color mappings
      headerBg: '#0a0a0a',        // Very dark header
      pptxText: '#FF9900',        // Amazon orange for file identification
      pptxFile: '#FF9900',        // Amazon orange for file identification
      blueFolder: '#569cd6',      // Keep blue for folders
      regularFile: '#ffffff',     // White for regular files
      restoredBadgeColor: '#000000',
      restoredBadgeBg: '#ffffff',
      noFolderText: '#ffffff',    // White for no folder message
    };
  } else {
    return {
      // Light theme - clean and professional
      bg: '#ffffff',
      bgSecondary: '#f8f8f8',
      bgTertiary: '#f1f1f1',
      
      text: '#333333',
      textSecondary: '#666666',
      textMuted: '#999999',
      
      // Light theme note type colors - more muted but still distinct
      developerNotesColor: '#0066cc',    // Darker blue
      instructorNotesColor: '#cc6600',   // Darker orange
      studentNotesColor: '#008844',      // Darker green
      referencesColor: '#006666',        // Darker teal
      scriptColor: '#cc8800',            // Darker yellow
      altTextColor: '#8844cc',           // Darker purple
      
      border: '#e1e1e1',
      inputBg: '#ffffff',
      inputBorder: '#d1d1d1',
      inputText: '#333333',
      
      buttonText: '#666666',
      buttonHover: '#f0f0f0',
      
      titleAccent: '#0066cc',
      bulletAccent: '#cc6600',
      urlAccent: '#006666',
      codeAccent: '#cc8800',
      
      // Legacy color mappings for existing components
      headerBg: '#f1f1f1',         // Header backgrounds
      pptxText: '#d84315',         // PPTX file text (burnt umber - warm, bright orange-brown)
      pptxFile: '#d84315',         // PPTX file icons (burnt umber - warm, bright orange-brown)
      blueFolder: '#0066cc',       // Folder icons (blue)
      regularFile: '#666666',      // Regular file icons
      restoredBadgeColor: '#ffffff', // Badge text
      restoredBadgeBg: '#006666',  // Badge background (teal)
      noFolderText: '#999999',     // No folder message text
    };
  }
}; 