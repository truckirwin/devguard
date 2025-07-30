export interface PPTFile {
  id: number;  // Keep for backward compatibility
  tracking_id: string;  // New robust identifier
  name: string;
  path: string;
  uploadedAt: string;
}

export interface NoteVersion {
  id: number;
  pptFileId: number;
  slideNumber: number;
  content: string;
  version: string;
  createdAt: string;
  updatedAt: string;
}

export interface SlideContent {
  slideNumber: number;
  title: string;
  content: string;
  altText: string[];
  speakerNotes: string;
}

export interface AIResponse {
  success: boolean;
  message: string;
  content?: string;
}

export interface Slide {
  id: number;
  pptFileId: number;
  slideNumber: number;
  content: string;
  createdAt: string;
  updatedAt: string;
}

export interface User {
  id: number;
  username: string;
  homeDirectory: string;
}
