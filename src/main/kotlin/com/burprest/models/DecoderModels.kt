package com.burprest.models

import kotlinx.serialization.Serializable

@Serializable
data class EncodeRequest(
    val data: String,
    val encoding: String,
)

@Serializable
data class EncodeResponse(
    val result: String,
    val encoding: String,
)

@Serializable
data class DecodeRequest(
    val data: String,
    val encoding: String? = null,
)

@Serializable
data class DecodeResponse(
    val result: String,
    val encoding: String,
)

@Serializable
data class HashRequest(
    val data: String,
    val algorithm: String,
)

@Serializable
data class HashResponse(
    val result: String,
    val algorithm: String,
)

@Serializable
data class SmartDecodeResponse(
    val result: String,
    val steps: List<DecodeStep>,
)

@Serializable
data class DecodeStep(
    val encoding: String,
    val result: String,
)
