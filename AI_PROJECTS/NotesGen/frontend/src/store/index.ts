import create from 'zustand';
import { persist } from 'zustand/middleware';
import { PPTFile, NoteVersion, SlideContent } from '../types/ppt';

interface SlideImageState {
  slide_number: number;
  hasRenderedImage: boolean;
  isProcessing: boolean;
  thumbnailUrl?: string;
  fullImageUrl?: string;
  localThumbnailUrl?: string; // For immediate local thumbnails
  hasLocalThumbnail?: boolean; // Flag for local thumbnail availability
}

interface Store {
  selectedPPT: PPTFile | null;
  slides: SlideContent[];
  setSelectedPPT: (ppt: PPTFile | null) => void;
  setSlides: (slides: SlideContent[]) => void;
  selectedSlide: number | null;
  setSelectedSlide: (slideNumber: number | null) => void;
  selectedSlideIndex: number;
  setSelectedSlideIndex: (index: number) => void;
  noteContent: string;
  setNoteContent: (content: string) => void;
  currentNoteVersion: NoteVersion | null;
  setCurrentNoteVersion: (version: NoteVersion | null) => void;
  lastDirectoryHandle: any | null;
  lastDirectoryPath: string | null;
  lastSelectedPPTPath: string | null;
  lastSelectedPPTName: string | null;
  expandedDirectories: Set<string>;
  setLastDirectory: (handle: any, path: string) => void;
  setLastSelectedPPT: (path: string, name: string) => void;
  addExpandedDirectory: (path: string) => void;
  removeExpandedDirectory: (path: string) => void;
  isDirectoryExpanded: (path: string) => boolean;
  clearExpandedDirectories: () => void;
  slideImages: Record<string, SlideImageState>;
  setSlideImageState: (pptIdentifier: string | number, slideNumber: number, state: Partial<SlideImageState>) => void;
  setLocalThumbnail: (pptIdentifier: string | number, slideNumber: number, thumbnailUrl: string) => void;
  clearSlideImages: (pptIdentifier: string | number) => void;
  processingStatus: {
    isProcessing: boolean;
    totalSlides: number;
    processedSlides: number;
    currentBatch: number;
  };
  setProcessingStatus: (status: Partial<Store['processingStatus']>) => void;
  bulkProcessingStatus: {
    isProcessing: boolean;
    jobId?: string;
    status: string;
    totalSlides: number;
    completedSlides: number;
    failedSlides: number;
    currentSlide?: number;    // Real-time current slide being processed
    progress?: number;        // Real-time progress percentage (0-100)
    error?: string;
  };
  setBulkProcessingStatus: (status: Partial<Store['bulkProcessingStatus']>) => void;
}

export const useStore = create<Store>()(
  persist(
    (set, get) => ({
      selectedPPT: null,
      slides: [],
      setSelectedPPT: (ppt) => set({ selectedPPT: ppt }),
      setSlides: (slides) => set({ slides }),
      selectedSlide: null,
      setSelectedSlide: (slideNumber) => set({ selectedSlide: slideNumber }),
      selectedSlideIndex: 0,
      setSelectedSlideIndex: (index) => set({ selectedSlideIndex: index }),
      noteContent: '',
      setNoteContent: (content) => set({ noteContent: content }),
      currentNoteVersion: null,
      setCurrentNoteVersion: (version) => set({ currentNoteVersion: version }),
      lastDirectoryHandle: null,
      lastDirectoryPath: null,
      lastSelectedPPTPath: null,
      lastSelectedPPTName: null,
      expandedDirectories: new Set<string>(),
      setLastDirectory: (handle, path) => set({ 
        lastDirectoryHandle: handle, 
        lastDirectoryPath: path 
      }),
      setLastSelectedPPT: (path, name) => set({
        lastSelectedPPTPath: path,
        lastSelectedPPTName: name
      }),
      addExpandedDirectory: (path) => set((store) => {
        const newExpandedDirectories = new Set(store.expandedDirectories);
        newExpandedDirectories.add(path);
        return { expandedDirectories: newExpandedDirectories };
      }),
      removeExpandedDirectory: (path) => set((store) => {
        const newExpandedDirectories = new Set(store.expandedDirectories);
        newExpandedDirectories.delete(path);
        return { expandedDirectories: newExpandedDirectories };
      }),
      isDirectoryExpanded: (path) => get().expandedDirectories.has(path),
      clearExpandedDirectories: () => set({ expandedDirectories: new Set<string>() }),
      slideImages: {},
      setSlideImageState: (pptIdentifier, slideNumber, state) => set((store) => {
        const key = `${pptIdentifier}-${slideNumber}`;
        const existingState = store.slideImages[key] || {
          slide_number: slideNumber,
          hasRenderedImage: false,
          isProcessing: false,
        };
        return {
          slideImages: {
            ...store.slideImages,
            [key]: {
              ...existingState,
              ...state,
            }
          }
        };
      }),
      setLocalThumbnail: (pptIdentifier, slideNumber, thumbnailUrl) => set((store) => {
        const key = `${pptIdentifier}-${slideNumber}`;
        const existingState = store.slideImages[key] || {
          slide_number: slideNumber,
          hasRenderedImage: false,
          isProcessing: false,
        };
        return {
          slideImages: {
            ...store.slideImages,
            [key]: {
              ...existingState,
              localThumbnailUrl: thumbnailUrl,
              hasLocalThumbnail: true,
            }
          }
        };
      }),
      clearSlideImages: (pptIdentifier) => set((store) => {
        const newSlideImages = { ...store.slideImages };
        Object.keys(newSlideImages).forEach(key => {
          if (key.startsWith(`${pptIdentifier}-`)) {
            delete newSlideImages[key];
          }
        });
        return { slideImages: newSlideImages };
      }),
      processingStatus: {
        isProcessing: false,
        totalSlides: 0,
        processedSlides: 0,
        currentBatch: 0,
      },
      setProcessingStatus: (status) => set((store) => ({
        processingStatus: { ...store.processingStatus, ...status }
      })),
      bulkProcessingStatus: {
        isProcessing: false,
        status: 'idle',
        totalSlides: 0,
        completedSlides: 0,
        failedSlides: 0,
      },
      setBulkProcessingStatus: (status) => set((store) => ({
        bulkProcessingStatus: { ...store.bulkProcessingStatus, ...status }
      })),
    }),
    {
      name: 'notesgen-storage',
      partialize: (state) => ({
        lastDirectoryPath: state.lastDirectoryPath,
        lastSelectedPPTPath: state.lastSelectedPPTPath,
        lastSelectedPPTName: state.lastSelectedPPTName,
        expandedDirectories: Array.from(state.expandedDirectories), // Convert Set to Array for serialization
      }),
      onRehydrateStorage: () => (state) => {
        console.log('🔄 Store rehydrated from localStorage:', {
          lastDirectoryPath: state?.lastDirectoryPath,
          lastSelectedPPTPath: state?.lastSelectedPPTPath,
          lastSelectedPPTName: state?.lastSelectedPPTName,
          expandedDirectories: state?.expandedDirectories
        });
        if (state && state.expandedDirectories) {
          // Convert Array back to Set after rehydration
          state.expandedDirectories = new Set(state.expandedDirectories as any);
        }
      },
    }
  )
);
