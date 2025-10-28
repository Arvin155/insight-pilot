// docs.js
const API_BASE_URL = '/api'

export const getDocumentList = async (knowledgeId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/docs/document_list?knowledge_id=${knowledgeId}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json'
            }
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        return await response.json()
    } catch (error) {
        console.error('获取文档列表失败:', error)
        throw error
    }
}

export const uploadDocuments = async (knowledgeId, files) => {
    try {
        const formData = new FormData()
        files.forEach(file => {
            formData.append('files', file)
        })

        const response = await fetch(`${API_BASE_URL}/docs/upload_documents?kb_id=${knowledgeId}`, {
            method: 'POST',
            headers: {
                'accept': 'application/json'
            },
            body: formData
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        return await response.json()
    } catch (error) {
        console.error('上传文档失败:', error)
        throw error
    }
}

export const getDocumentChunks = async (documentId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/docs/chunks/${documentId}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json'
            }
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        return await response.json()
    } catch (error) {
        console.error('获取文档分块失败:', error)
        throw error
    }
}

export const deleteDocument = async (documentId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/docs/delete_document/${documentId}`, {
            method: 'DELETE',
            headers: {
                'accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('删除文档失败:', error);
        throw error;
    }
}

export const downloadDocument = async (documentId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/docs/download/${documentId}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response;
    } catch (error) {
        console.error('下载文档失败:', error);
        throw error;
    }
}