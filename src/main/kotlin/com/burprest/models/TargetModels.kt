package com.burprest.models

import kotlinx.serialization.Serializable

@Serializable
data class SitemapResponse(
    val entries: List<SitemapEntry>,
    val total: Int,
)

@Serializable
data class SitemapEntry(
    val url: String,
    val method: String,
    val statusCode: Int? = null,
    val mimeType: String? = null,
)

@Serializable
data class ScopeResponse(
    val includes: List<String>,
    val excludes: List<String>,
)

@Serializable
data class SetScopeRequest(
    val includes: List<String>,
    val excludes: List<String> = emptyList(),
)

@Serializable
data class AddScopeRequest(
    val url: String,
)

@Serializable
data class ScopeCheckRequest(
    val url: String,
)

@Serializable
data class ScopeCheckResponse(
    val url: String,
    val inScope: Boolean,
)
