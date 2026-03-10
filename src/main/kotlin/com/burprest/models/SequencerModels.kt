package com.burprest.models

import kotlinx.serialization.Serializable

@Serializable
data class SequencerStartRequest(
    val requestId: Int? = null,
    val request: HttpRequestData? = null,
    val tokenLocation: String? = null,
)

@Serializable
data class SequencerStartResponse(
    val captureId: String,
    val status: String,
)

@Serializable
data class SequencerStatusResponse(
    val captureId: String,
    val status: String,
    val tokensCaptured: Int = 0,
)

@Serializable
data class SequencerAnalyzeRequest(
    val tokens: List<String>? = null,
)

@Serializable
data class SequencerResultsResponse(
    val captureId: String,
    val effectiveEntropyBits: Double,
    val reliabilityPercent: Double,
    val sampleSize: Int,
    val fipsOverallPassed: Boolean,
)
