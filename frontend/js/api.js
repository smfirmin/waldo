// API communication module
class ApiClient {
    constructor() {
        this.baseUrl = '';
    }

    // Extract locations from URL or text
    async extractLocations(input) {
        const response = await fetch('/api/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ input: input })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            
            // Handle rate limit errors specially
            if (response.status === 429 || (errorData.error_code && errorData.error_code === 'RATE_LIMIT_EXCEEDED')) {
                const retryAfter = response.headers.get('Retry-After') || errorData.retry_after || 60;
                throw new Error(`⏰ API rate limit exceeded. Please try again in ${retryAfter} seconds.\n\nTip: The Gemini API has usage limits. You can try again shortly.`);
            }
            
            throw new Error(errorData.message || errorData.error || 'Failed to extract locations');
        }
        
        const data = await response.json();
        return data;
    }
}

// Export for global use
window.ApiClient = ApiClient;