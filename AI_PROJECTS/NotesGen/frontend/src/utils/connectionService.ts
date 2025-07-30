interface HealthResponse {
  status: string;
}

interface ConnectionStatus {
  isConnected: boolean;
  lastChecked: Date;
  retryCount: number;
  error?: string;
}

class ConnectionService {
  private static instance: ConnectionService;
  private status: ConnectionStatus = {
    isConnected: false,
    lastChecked: new Date(),
    retryCount: 0
  };
  
  private apiBase: string;
  private maxRetries = 5;
  private retryDelay = 2000; // 2 seconds
  private healthCheckInterval = 30000; // 30 seconds
  private healthCheckTimer?: NodeJS.Timeout;

  private constructor() {
    this.apiBase = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.startHealthChecking();
  }

  public static getInstance(): ConnectionService {
    if (!ConnectionService.instance) {
      ConnectionService.instance = new ConnectionService();
    }
    return ConnectionService.instance;
  }

  /**
   * Check if backend is healthy
   */
  public async checkHealth(): Promise<boolean> {
    try {
      console.log('🔍 Checking backend health...');
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

      const response = await fetch(`${this.apiBase}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data: HealthResponse = await response.json();
        const isHealthy = data.status === 'healthy';
        
        this.updateStatus(isHealthy, isHealthy ? undefined : `Unhealthy response: ${data.status}`);
        
        if (isHealthy) {
          console.log('✅ Backend is healthy');
          this.status.retryCount = 0; // Reset retry count on success
        }
        
        return isHealthy;
      } else {
        const errorMsg = `HTTP ${response.status}: ${response.statusText}`;
        this.updateStatus(false, errorMsg);
        console.error('❌ Backend health check failed:', errorMsg);
        return false;
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      this.updateStatus(false, errorMsg);
      console.error('❌ Backend health check error:', errorMsg);
      return false;
    }
  }

  /**
   * Ensure backend is connected before making API calls
   */
  public async ensureConnection(): Promise<boolean> {
    // If we recently confirmed connection, skip check
    const timeSinceLastCheck = Date.now() - this.status.lastChecked.getTime();
    if (this.status.isConnected && timeSinceLastCheck < 10000) { // 10 seconds
      return true;
    }

    console.log('🔄 Ensuring backend connection...');
    
    // Try immediate health check
    if (await this.checkHealth()) {
      return true;
    }

    // If failed, try with retries
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      console.log(`🔄 Connection attempt ${attempt}/${this.maxRetries}...`);
      
      if (await this.checkHealth()) {
        console.log('✅ Backend connection established');
        return true;
      }

      if (attempt < this.maxRetries) {
        console.log(`⏳ Waiting ${this.retryDelay}ms before retry...`);
        await this.delay(this.retryDelay);
        this.retryDelay = Math.min(this.retryDelay * 1.5, 10000); // Exponential backoff, max 10s
      }
    }

    console.error('❌ Failed to establish backend connection after retries');
    return false;
  }

  /**
   * Make a robust API call with connection checking
   */
  public async apiCall<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    // Ensure backend is connected first
    const isConnected = await this.ensureConnection();
    if (!isConnected) {
      throw new Error('Backend is not available. Please check your connection and try again.');
    }

    const url = `${this.apiBase}${endpoint}`;
    console.log(`🌐 Making API call: ${options.method || 'GET'} ${url}`);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        // Mark as disconnected if we get server errors
        if (response.status >= 500) {
          this.updateStatus(false, `Server error: ${response.status}`);
        }
        
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ API call successful');
      
      // Update connection status on successful API call
      this.updateStatus(true);
      
      return data;
    } catch (error) {
      // Mark as disconnected on network errors
      if (error instanceof Error && (
        error.name === 'AbortError' || 
        error.message.includes('fetch') ||
        error.message.includes('NetworkError')
      )) {
        this.updateStatus(false, error.message);
      }
      
      console.error('❌ API call failed:', error);
      throw error;
    }
  }

  /**
   * Get current connection status
   */
  public getStatus(): ConnectionStatus {
    return { ...this.status };
  }

  /**
   * Start periodic health checking
   */
  private startHealthChecking(): void {
    // Initial health check
    this.checkHealth();

    // Set up periodic health checks
    this.healthCheckTimer = setInterval(() => {
      this.checkHealth();
    }, this.healthCheckInterval);
  }

  /**
   * Stop health checking (cleanup)
   */
  public stopHealthChecking(): void {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = undefined;
    }
  }

  /**
   * Update connection status
   */
  private updateStatus(isConnected: boolean, error?: string): void {
    this.status = {
      isConnected,
      lastChecked: new Date(),
      retryCount: this.status.retryCount + (isConnected ? 0 : 1),
      error
    };
  }

  /**
   * Utility delay function
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Export singleton instance
export const connectionService = ConnectionService.getInstance();

// Export types
export type { ConnectionStatus }; 