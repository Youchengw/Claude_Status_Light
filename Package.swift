// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ClaudeLight",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(
            name: "ClaudeLight",
            targets: ["ClaudeLight"]
        )
    ],
    targets: [
        .executableTarget(
            name: "ClaudeLight",
            path: "Sources"
        )
    ]
)
