package com.burprest.models

import kotlinx.serialization.Serializable

@Serializable
data class SendRequest(
    val request: HttpRequestData? = null,
    val requestId: Int? = null,
    val modifications: RequestModifications? = null,
)

@Serializable
data class RequestModifications(
    val headers: Map<String, String>? = null,
    val body: String? = null,
    val method: String? = null,
    val path: String? = null,
)

@Serializable
data class SendResponse(
    val request: HttpRequestData,
    val response: HttpResponseData,
    val durationMs: Long,
)

@Serializable
data class BatchSendRequest(
    val requests: List<SendRequest>,
)

@Serializable
data class BatchSendResponse(
    val results: List<SendResponse>,
    val totalDurationMs: Long,
)

@Serializable
data class CreateTabRequest(
    val name: String? = null,
    val request: HttpRequestData? = null,
    val requestId: Int? = null,
)

@Serializable
data class CreateTabResponse(
    val name: String,
    val created: Boolean,
)
