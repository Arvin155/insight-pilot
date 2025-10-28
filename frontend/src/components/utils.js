export function toast(message,type="success") {
    ElMessage({
        showClose: true,
        message: message,
        type: type,
    })
}