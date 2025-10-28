const API_BASE_URL = '/api'


export const login = async (loginData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/user/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        return data
    } catch (error) {
        throw new Error(`登录请求失败: ${error.message}`)
    }
}

// 添加手机号唯一性校验接口
export const checkMobile = async (mobile_phone) => {
    const response = await fetch(`${API_BASE_URL}/user/check-mobile?mobile_phone=${mobile_phone}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })

    if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || '校验失败')
    }

    return await response.json()
}

// 添加注册接口
export const register = async (registerData) => {
    try {
        const response = await fetch(`${API_BASE_URL}/user/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(registerData)
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        return data
    } catch (error) {
        throw new Error(`注册请求失败: ${error.message}`)
    }
}
