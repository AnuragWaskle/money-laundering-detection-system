import axios from 'axios';

// Create an Axios instance with a base URL.
// This makes it easy to change the API endpoint in one place.
const apiClient = axios.create({
  baseURL: 'http://localhost:5001/api', // The address of our Flask backend
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Uploads a CSV file to the backend for processing.
 * @param {File} file - The CSV file to upload.
 * @returns {Promise<Object>} The response data from the server.
 */
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading file:', error.response ? error.response.data : error.message);
    throw error;
  }
};

/**
 * Fetches graph data for a specific account ID.
 * @param {string} accountId - The ID of the account to visualize.
 * @returns {Promise<Object>} The graph data (nodes and links).
 */
export const getGraphDataForAccount = async (accountId) => {
  try {
    const response = await apiClient.get(`/graph-data`, {
      params: { account_id: accountId },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching graph data:', error.response ? error.response.data : error.message);
    throw error;
  }
};

/**
 * Sends a single transaction object to the backend for a fraud prediction.
 * @param {Object} transactionData - The transaction data.
 * @returns {Promise<Object>} The prediction result.
 */
export const getPrediction = async (transactionData) => {
    try {
        const response = await apiClient.post('/predict', transactionData);
        return response.data;
    } catch (error) {
        console.error('Error getting prediction:', error.response ? error.response.data : error.message);
        throw error;
    }
};
