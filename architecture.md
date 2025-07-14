# Brain Document AI - Architecture Diagrams

This document contains draw.io compatible diagrams showing the architecture of the Brain Document AI system.

## System Architecture Diagram

Copy and paste this code into draw.io (https://app.diagrams.net/):

```xml
<mxfile host="app.diagrams.net" modified="2025-07-14T20:00:00.000Z" agent="5.0" version="21.6.2" etag="brain-architecture" type="device">
  <diagram name="Brain Architecture" id="brain-system-architecture">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- User -->
        <mxCell id="user-1" value="User" style="shape=actor;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="40" y="350" width="40" height="60" as="geometry" />
        </mxCell>
        
        <!-- Frontend Container -->
        <mxCell id="frontend-container" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;" vertex="1" parent="1">
          <mxGeometry x="140" y="280" width="200" height="200" as="geometry" />
        </mxCell>
        
        <mxCell id="frontend-label" value="Frontend (Port 3001)" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="140" y="250" width="200" height="30" as="geometry" />
        </mxCell>
        
        <!-- React App -->
        <mxCell id="react-app" value="React App&lt;br&gt;(TypeScript + Material-UI)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="160" y="300" width="160" height="60" as="geometry" />
        </mxCell>
        
        <!-- Nginx -->
        <mxCell id="nginx" value="nginx&lt;br&gt;(Reverse Proxy)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="160" y="390" width="160" height="60" as="geometry" />
        </mxCell>
        
        <!-- Backend Container -->
        <mxCell id="backend-container" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;" vertex="1" parent="1">
          <mxGeometry x="400" y="180" width="300" height="400" as="geometry" />
        </mxCell>
        
        <mxCell id="backend-label" value="Backend API (Port 8001)" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="400" y="150" width="300" height="30" as="geometry" />
        </mxCell>
        
        <!-- FastAPI -->
        <mxCell id="fastapi" value="FastAPI&lt;br&gt;(REST API + WebSocket)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="470" y="200" width="160" height="60" as="geometry" />
        </mxCell>
        
        <!-- Auth Module -->
        <mxCell id="auth-module" value="JWT Auth&lt;br&gt;(30 min tokens)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e6d0de;strokeColor=#996185;" vertex="1" parent="1">
          <mxGeometry x="420" y="280" width="120" height="50" as="geometry" />
        </mxCell>
        
        <!-- Document Processor -->
        <mxCell id="doc-processor" value="Document&lt;br&gt;Processor" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e6d0de;strokeColor=#996185;" vertex="1" parent="1">
          <mxGeometry x="560" y="280" width="120" height="50" as="geometry" />
        </mxCell>
        
        <!-- Services -->
        <mxCell id="embeddings-service" value="Embeddings&lt;br&gt;Service&lt;br&gt;(Mock/Bedrock)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="420" y="350" width="120" height="60" as="geometry" />
        </mxCell>
        
        <mxCell id="llm-service" value="LLM Service&lt;br&gt;(Mock/Bedrock)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="560" y="350" width="120" height="60" as="geometry" />
        </mxCell>
        
        <mxCell id="vector-store" value="Vector Store&lt;br&gt;Service" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="420" y="430" width="120" height="60" as="geometry" />
        </mxCell>
        
        <mxCell id="redaction-service" value="Redaction API&lt;br&gt;(polcn/redact)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="560" y="430" width="120" height="60" as="geometry" />
        </mxCell>
        
        <!-- Data Layer Container -->
        <mxCell id="data-container" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;" vertex="1" parent="1">
          <mxGeometry x="760" y="180" width="350" height="400" as="geometry" />
        </mxCell>
        
        <mxCell id="data-label" value="Data Layer" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="760" y="150" width="350" height="30" as="geometry" />
        </mxCell>
        
        <!-- PostgreSQL -->
        <mxCell id="postgresql" value="PostgreSQL + pgvector&lt;br&gt;(Port 5433)&lt;br&gt;&lt;br&gt;Tables:&lt;br&gt;- users&lt;br&gt;- documents&lt;br&gt;- chunks&lt;br&gt;- audit_log" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="790" y="200" width="140" height="140" as="geometry" />
        </mxCell>
        
        <!-- Redis -->
        <mxCell id="redis" value="Redis Cache&lt;br&gt;(Port 6379)&lt;br&gt;&lt;br&gt;- Session data&lt;br&gt;- API cache" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffe6cc;strokeColor=#d79b00;" vertex="1" parent="1">
          <mxGeometry x="950" y="200" width="130" height="100" as="geometry" />
        </mxCell>
        
        <!-- MinIO -->
        <mxCell id="minio" value="MinIO S3&lt;br&gt;(Ports 9000/9001)&lt;br&gt;&lt;br&gt;Bucket:&lt;br&gt;brain-documents" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#e1d5e7;strokeColor=#9673a6;" vertex="1" parent="1">
          <mxGeometry x="790" y="380" width="140" height="100" as="geometry" />
        </mxCell>
        
        <!-- AWS Bedrock (External) -->
        <mxCell id="bedrock" value="AWS Bedrock&lt;br&gt;(External)&lt;br&gt;&lt;br&gt;- Claude Instant&lt;br&gt;- Titan Embeddings" style="ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="950" y="380" width="140" height="100" as="geometry" />
        </mxCell>
        
        <!-- Connections -->
        <mxCell id="edge1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="user-1" target="react-app">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="react-app" target="nginx">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge3" value="/api/*" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="nginx" target="fastapi">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="fastapi" target="auth-module">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="fastapi" target="doc-processor">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="doc-processor" target="embeddings-service">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="fastapi" target="llm-service">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge8" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="fastapi" target="vector-store">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge9" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="doc-processor" target="redaction-service">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge10" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="vector-store" target="postgresql">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge11" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="auth-module" target="postgresql">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge12" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="fastapi" target="redis">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge13" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="doc-processor" target="minio">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge14" value="Falls back to mock" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;" edge="1" parent="1" source="embeddings-service" target="bedrock">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="edge15" value="Falls back to mock" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;" edge="1" parent="1" source="llm-service" target="bedrock">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Document Processing Flow Diagram

Copy and paste this code into draw.io:

```xml
<mxfile host="app.diagrams.net" modified="2025-07-14T20:00:00.000Z" agent="5.0" version="21.6.2" etag="brain-doc-flow" type="device">
  <diagram name="Document Processing Flow" id="brain-document-flow">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- Start -->
        <mxCell id="start" value="User Uploads&lt;br&gt;Document" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="120" height="80" as="geometry" />
        </mxCell>
        
        <!-- Auth Check -->
        <mxCell id="auth-check" value="JWT Auth&lt;br&gt;Validation" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="200" y="30" width="100" height="100" as="geometry" />
        </mxCell>
        
        <!-- Store Metadata -->
        <mxCell id="store-metadata" value="Store Document&lt;br&gt;Metadata in DB&lt;br&gt;(with user_id)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="340" y="40" width="140" height="80" as="geometry" />
        </mxCell>
        
        <!-- Extract Text -->
        <mxCell id="extract-text" value="Extract Text&lt;br&gt;(PDF/DOCX/TXT)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="520" y="40" width="140" height="80" as="geometry" />
        </mxCell>
        
        <!-- Redact -->
        <mxCell id="redact" value="Redact PII&lt;br&gt;(polcn/redact API)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="700" y="40" width="140" height="80" as="geometry" />
        </mxCell>
        
        <!-- Redact Decision -->
        <mxCell id="redact-decision" value="Redaction&lt;br&gt;Success?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="880" y="30" width="100" height="100" as="geometry" />
        </mxCell>
        
        <!-- Store S3 -->
        <mxCell id="store-s3" value="Store Document&lt;br&gt;in MinIO/S3" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;" vertex="1" parent="1">
          <mxGeometry x="340" y="180" width="140" height="80" as="geometry" />
        </mxCell>
        
        <!-- Chunk Text -->
        <mxCell id="chunk-text" value="Split into&lt;br&gt;Text Chunks&lt;br&gt;(512 tokens)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="520" y="180" width="140" height="80" as="geometry" />
        </mxCell>
        
        <!-- Generate Embeddings -->
        <mxCell id="gen-embeddings" value="Generate&lt;br&gt;Embeddings" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="700" y="180" width="140" height="80" as="geometry" />
        </mxCell>
        
        <!-- Bedrock Decision -->
        <mxCell id="bedrock-decision" value="Bedrock&lt;br&gt;Available?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="880" y="170" width="100" height="100" as="geometry" />
        </mxCell>
        
        <!-- Mock Embeddings -->
        <mxCell id="mock-embeddings" value="Generate Mock&lt;br&gt;Embeddings&lt;br&gt;(Hash-based)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e6d0de;strokeColor=#996185;" vertex="1" parent="1">
          <mxGeometry x="1020" y="180" width="120" height="80" as="geometry" />
        </mxCell>
        
        <!-- Store Vectors -->
        <mxCell id="store-vectors" value="Store Vectors&lt;br&gt;in PostgreSQL&lt;br&gt;(pgvector)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="700" y="320" width="140" height="80" as="geometry" />
        </mxCell>
        
        <!-- Update Status -->
        <mxCell id="update-status" value="Update Document&lt;br&gt;Status to&lt;br&gt;'processed'" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="520" y="320" width="140" height="80" as="geometry" />
        </mxCell>
        
        <!-- End Success -->
        <mxCell id="end-success" value="Document Ready&lt;br&gt;for Search" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="340" y="320" width="120" height="80" as="geometry" />
        </mxCell>
        
        <!-- End Fail -->
        <mxCell id="end-fail" value="Upload Failed&lt;br&gt;(401 Unauthorized)" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="190" y="180" width="120" height="80" as="geometry" />
        </mxCell>
        
        <!-- Flow Arrows -->
        <mxCell id="flow1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="start" target="auth-check">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow2" value="Valid" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="auth-check" target="store-metadata">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow3" value="Invalid" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="auth-check" target="end-fail">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="store-metadata" target="extract-text">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="extract-text" target="redact">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="redact" target="redact-decision">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow7" value="Success" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="redact-decision" target="store-s3">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="930" y="150" />
              <mxPoint x="410" y="150" />
            </Array>
          </mxGeometry>
        </mxCell>
        
        <mxCell id="flow8" value="Fail (use original)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;" edge="1" parent="1" source="redact-decision" target="store-s3">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="930" y="160" />
              <mxPoint x="410" y="160" />
            </Array>
          </mxGeometry>
        </mxCell>
        
        <mxCell id="flow9" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="store-s3" target="chunk-text">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow10" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="chunk-text" target="gen-embeddings">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow11" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="gen-embeddings" target="bedrock-decision">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow12" value="No" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="bedrock-decision" target="mock-embeddings">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow13" value="Yes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="bedrock-decision" target="store-vectors">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="930" y="300" />
              <mxPoint x="770" y="300" />
            </Array>
          </mxGeometry>
        </mxCell>
        
        <mxCell id="flow14" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="mock-embeddings" target="store-vectors">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1080" y="300" />
              <mxPoint x="770" y="300" />
            </Array>
          </mxGeometry>
        </mxCell>
        
        <mxCell id="flow15" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="store-vectors" target="update-status">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="flow16" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="update-status" target="end-success">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Authentication Flow Diagram

Copy and paste this code into draw.io:

```xml
<mxfile host="app.diagrams.net" modified="2025-07-14T20:00:00.000Z" agent="5.0" version="21.6.2" etag="brain-auth-flow" type="device">
  <diagram name="Authentication Flow" id="brain-auth-flow">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- User -->
        <mxCell id="user" value="User" style="shape=actor;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="40" y="160" width="40" height="60" as="geometry" />
        </mxCell>
        
        <!-- Frontend -->
        <mxCell id="frontend" value="Frontend&lt;br&gt;(React)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="140" y="150" width="100" height="80" as="geometry" />
        </mxCell>
        
        <!-- Login Endpoint -->
        <mxCell id="login-endpoint" value="/api/v1/auth/login" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="300" y="150" width="140" height="80" as="geometry" />
        </mxCell>
        
        <!-- Auth Service -->
        <mxCell id="auth-service" value="Auth Service&lt;br&gt;(JWT + bcrypt)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e6d0de;strokeColor=#996185;" vertex="1" parent="1">
          <mxGeometry x="500" y="150" width="120" height="80" as="geometry" />
        </mxCell>
        
        <!-- Database -->
        <mxCell id="database" value="PostgreSQL&lt;br&gt;users table" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="680" y="140" width="100" height="100" as="geometry" />
        </mxCell>
        
        <!-- Protected Endpoint -->
        <mxCell id="protected-endpoint" value="Protected&lt;br&gt;Endpoint&lt;br&gt;(e.g., /documents)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="300" y="300" width="140" height="80" as="geometry" />
        </mxCell>
        
        <!-- Auth Middleware -->
        <mxCell id="auth-middleware" value="Auth Middleware&lt;br&gt;(Token Validation)" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="500" y="290" width="120" height="100" as="geometry" />
        </mxCell>
        
        <!-- Steps -->
        <mxCell id="step1" value="1. Login Request&lt;br&gt;(username, password)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="user" target="frontend">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="step2" value="2. POST credentials" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="frontend" target="login-endpoint">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="step3" value="3. Validate" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="login-endpoint" target="auth-service">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="step4" value="4. Check user" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="auth-service" target="database">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="step5" value="5. Return JWT&lt;br&gt;(30 min expiry)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;curved=1;" edge="1" parent="1" source="auth-service" target="frontend">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="560" y="100" />
              <mxPoint x="190" y="100" />
            </Array>
          </mxGeometry>
        </mxCell>
        
        <mxCell id="step6" value="6. Store token&lt;br&gt;in localStorage" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;" vertex="1" parent="1">
          <mxGeometry x="140" y="240" width="100" height="40" as="geometry" />
        </mxCell>
        
        <mxCell id="step7" value="7. Request with&lt;br&gt;Bearer token" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="frontend" target="protected-endpoint">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="step8" value="8. Validate token" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="protected-endpoint" target="auth-middleware">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
        <mxCell id="step9" value="Valid" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="auth-middleware" target="database">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="680" y="340" />
            </Array>
          </mxGeometry>
        </mxCell>
        
        <mxCell id="step10" value="Invalid" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;curved=1;" edge="1" parent="1" source="auth-middleware" target="frontend">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="560" y="420" />
              <mxPoint x="190" y="420" />
            </Array>
            <mxGeometry x="-0.1" y="10" relative="1" as="geometry">
              <mxPoint as="offset" />
            </mxGeometry>
          </mxGeometry>
        </mxCell>
        
        <mxCell id="error-text" value="401 Unauthorized&lt;br&gt;Redirect to login" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;" vertex="1" parent="1">
          <mxGeometry x="320" y="430" width="120" height="40" as="geometry" />
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Instructions for Using the Diagrams

1. Go to https://app.diagrams.net/ (draw.io)
2. Click "Create New Diagram" or "Open Existing Diagram"
3. In the editor, go to File > Import from > Device
4. Create a new file with `.drawio` extension
5. Copy the XML code for the diagram you want
6. Paste it into the file and save
7. Open the file in draw.io

Alternatively:
1. In draw.io, go to Extras > Edit Diagram
2. Replace the content with the XML code above
3. Click "Apply"

The diagrams show:
- **System Architecture**: Overall component layout and connections
- **Document Processing Flow**: Step-by-step document upload and processing
- **Authentication Flow**: JWT authentication process and token validation

You can modify colors, add more details, or export as PNG/SVG as needed.