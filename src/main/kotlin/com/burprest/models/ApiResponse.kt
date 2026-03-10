package com.burprest.models

import kotlinx.serialization.Serializable

@Serializable
data class ApiResponse<T>(
    val success: Boolean,
    val data: T? = null,
    val error: ApiError? = null,
) {
    companion object {
        fun <T> ok(data: T): ApiResponse<T> = ApiResponse(success = true, data = data)

        fun <T> error(code: String, message: String): ApiResponse<T> =
            ApiResponse(success = false, error = ApiError(code, message))
    }
}

@Serializable
data class ApiError(
    val code: String,
    val message: String,
)
