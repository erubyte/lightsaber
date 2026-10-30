// Subject cutout with Apple Vision: cutout <in> <out.png>
import Foundation
import Vision
import CoreImage
import AppKit

let args = CommandLine.arguments
let url = URL(fileURLWithPath: args[1])
guard let ci = CIImage(contentsOf: url, options: [.applyOrientationProperty: true]) else { fatalError("load") }
let handler = VNImageRequestHandler(ciImage: ci)
let req = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([req])
guard let obs = req.results?.first else { fatalError("no subject") }
let buf = try obs.generateMaskedImage(ofInstances: obs.allInstances, from: handler, croppedToInstancesExtent: true)
let out = CIImage(cvPixelBuffer: buf)
let ctx = CIContext()
try ctx.writePNGRepresentation(of: out, to: URL(fileURLWithPath: args[2]), format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
print("ok", out.extent.size)
