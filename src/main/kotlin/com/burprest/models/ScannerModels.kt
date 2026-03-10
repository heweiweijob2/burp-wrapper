package com.burprest.models

import kotlinx.serialization.Serializable

@Serializable
data class ScanRequest(
    val url: String,
    val config: ScanConfig = ScanConfig(),
)

@Serializable
data class ScanConfig(
    val crawlStrategy: String? = null,
    val auditOptimization: String? = null,
)

@Serializable
data class ScanStartResponse(
    val scanId: String,
    val status: String,
)

@Serializable
data class ScanStatusResponse(
    val scanId: String,
    val status: String,
    val crawlProgress: Int = 0,
    val auditProgress: Int = 0,
    val issueCount: Int = 0,
)

@Serializable
data class ScanIssue(
    val name: String,
    val url: String,
    val severity: String,
    val confidence: String,
    val detail: String? = null,
    val remediation: String? = null,
)

@Serializable
data class ScanIssuesResponse(
    val scanId: String,
    val issues: List<ScanIssue>,
    val total: Int,
)

@Serializable
data class IssueDefinition(
    val name: String,
    val typeIndex: Long,
    val description: String,
    val remediation: String,
)

@Serializable
data class IssueDefinitionsResponse(
    val definitions: List<IssueDefinition>,
    val total: Int,
)
