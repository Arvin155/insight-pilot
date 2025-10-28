// knowledge.js - 更新后的服务文件
const API_BASE_URL = '/api'

export const createKnowledge = async (data) => {
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge/create_knowledge`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        return await response.json()
    } catch (error) {
        console.error('创建知识库请求失败:', error)
        throw error
    }
}


export const getKnowledgeList = async (userId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge/list_knowledge?user_id=${userId}`, {
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
        console.error('获取知识库列表失败:', error)
        throw error
    }
}

export const updateKnowledge = async (data) => {
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge/update_knowledge`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        return await response.json()
    } catch (error) {
        console.error('更新知识库请求失败:', error)
        throw error
    }
}

export const updateKnowledgeStatus = async (data) => {
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge/update_status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        return await response.json()
    } catch (error) {
        console.error('更新知识库状态失败:', error)
        throw error
    }
}

