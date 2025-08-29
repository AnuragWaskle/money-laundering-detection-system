<<<<<<< HEAD
// import axios from 'axios';

// const apiClient = axios.create({
//   baseURL: 'http://localhost:5001/api',
//   headers: { 'Content-Type': 'application/json' },
// });

// export const uploadCsvFile = async (file, mapping) => {
//   const formData = new FormData();
//   formData.append('file', file);
//   formData.append('mapping', JSON.stringify(mapping));

//   try {
//     const response = await apiClient.post('/upload-csv', formData, {
//       headers: { 'Content-Type': 'multipart/form-data' },
//     });
//     return response.data;
//   } catch (error) {
//     console.error('Error uploading CSV file:', error.response ? error.response.data : error.message);
//     throw error;
//   }
// };

// export const uploadPdfFile = async (file) => {
//   const formData = new FormData();
//   formData.append('file', file);

//   try {
//     const response = await apiClient.post('/upload-pdf', formData, {
//       headers: { 'Content-Type': 'multipart/form-data' },
//     });
//     return response.data;
//   } catch (error) {
//     console.error('Error uploading PDF file:', error.response ? error.response.data : error.message);
//     throw error;
//   }
// };

// export const getGraphDataForAccount = async (accountId) => {
//   try {
//     const response = await apiClient.get(`/graph-data`, {
//       params: { account_id: accountId },
//     });
//     return response.data;
//   } catch (error) {
//     console.error('Error fetching graph data:', error.response ? error.response.data : error.message);
//     throw error;
//   }
// };

// export const getPrediction = async (transactionData) => {
//   try {
//     const response = await apiClient.post('/predict', transactionData);
//     return response.data;
//   } catch (error) {
//     console.error('Error getting prediction:', error.response ? error.response.data : error.message);
//     throw error;
//   }
// };

// export const getAccountSummary = async (accountId) => {
//   try {
//     const response = await apiClient.get(`/account-summary/${accountId}`);
//     return response.data;
//   } catch (error) {
//     console.error('Error fetching account summary:', error.response ? error.response.data : error.message);
//     throw error;
//   }
// };

// export const analyzeGraphWithGNN = async (accountId) => {
//   try {
//     const response = await apiClient.get(`/analyze-graph/${accountId}`);
//     return response.data;
//   } catch (error) {
//     console.error('Error analyzing graph with GNN:', error.response ? error.response.data : error.message);
//     throw error;
//   }
// };


=======
>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:5001/api',
  headers: { 'Content-Type': 'application/json' },
});

export const uploadCsvFile = async (file, mapping) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('mapping', JSON.stringify(mapping));
<<<<<<< HEAD
  const response = await apiClient.post('/upload-csv', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
  return response.data;
=======

  try {
    const response = await apiClient.post('/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading CSV file:', error.response ? error.response.data : error.message);
    throw error;
  }
>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
};

export const uploadPdfFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
<<<<<<< HEAD
  const response = await apiClient.post('/upload-pdf', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
  return response.data;
};

export const getGraphDataForAccount = async (accountId) => {
  const response = await apiClient.get(`/graph-data`, { params: { account_id: accountId } });
  return response.data;
};

export const getAccountSummary = async (accountId) => {
  const response = await apiClient.get(`/account-summary/${accountId}`);
  return response.data;
};

export const analyzeGraphWithGNN = async (accountId) => {
  const response = await apiClient.get(`/analyze-graph/${accountId}`);
  return response.data;
};

// --- NEW ANALYSIS FUNCTIONS ---
export const findCyclesInGraph = async () => {
  const response = await apiClient.get('/graph/find-cycles');
  return response.data;
};

export const findHighRiskNodesInGraph = async () => {
  const response = await apiClient.get('/graph/find-high-risk');
  return response.data;
};
=======

  try {
    const response = await apiClient.post('/upload-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading PDF file:', error.response ? error.response.data : error.message);
    throw error;
  }
};

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

export const getPrediction = async (transactionData) => {
  try {
    const response = await apiClient.post('/predict', transactionData);
    return response.data;
  } catch (error) {
    console.error('Error getting prediction:', error.response ? error.response.data : error.message);
    throw error;
  }
};

export const getAccountSummary = async (accountId) => {
  try {
    const response = await apiClient.get(`/account-summary/${accountId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching account summary:', error.response ? error.response.data : error.message);
    throw error;
  }
};

export const analyzeGraphWithGNN = async (accountId) => {
  try {
    const response = await apiClient.get(`/analyze-graph/${accountId}`);
    return response.data;
  } catch (error) {
    console.error('Error analyzing graph with GNN:', error.response ? error.response.data : error.message);
    throw error;
  }
};
>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
