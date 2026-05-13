import { useEffect, useRef, useState } from "react";
import axios from "axios";
import { diffLines } from "diff";

import {
  Send,
  Bot,
  User,
  Activity,
  Folder,
  FileText,
  ArrowLeft,
  Sparkles,
  Check,
  X,
  Terminal,
  Play,
} from "lucide-react";

import "./App.css";

function App() {
  const terminalSocketRef = useRef(null);

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Atlas Agent online.",
      traces: [],
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState(".");
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState("");
  const [editorOpen, setEditorOpen] = useState(true);

  const [editInstruction, setEditInstruction] = useState("");
  const [proposedContent, setProposedContent] = useState("");
  const [diffPreview, setDiffPreview] = useState([]);
  const [editLoading, setEditLoading] = useState(false);

  const [terminalCommand, setTerminalCommand] = useState("");
  const [terminalOutput, setTerminalOutput] = useState([]);
  const [terminalRunning, setTerminalRunning] = useState(false);

  useEffect(() => {
    loadFiles(".");
  }, []);

  async function loadFiles(path = ".") {
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/api/files/tree?path=${path}`
      );

      setFiles(res.data.items);
      setCurrentPath(path);
    } catch (err) {
      console.error(err);
    }
  }

  function goBackDirectory() {
    if (currentPath === ".") return;

    const parts = currentPath.split("/");
    parts.pop();

    const parent = parts.length === 0 ? "." : parts.join("/");
    loadFiles(parent);
  }

  async function openFile(path) {
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/api/files/read?path=${path}`
      );

      setSelectedFile(path);
      setFileContent(res.data.content);

      setProposedContent("");
      setDiffPreview([]);
      setEditInstruction("");

      setEditorOpen(true);
    } catch (err) {
      console.error(err);
    }
  }

  async function saveFile() {
    if (!selectedFile) return;

    try {
      await axios.post("http://127.0.0.1:8000/api/files/save", {
        path: selectedFile,
        content: fileContent,
      });

      alert("File saved.");
    } catch (err) {
      console.error(err);
      alert("Failed to save file.");
    }
  }

  async function proposeEdit() {
    if (!selectedFile || !editInstruction.trim()) return;

    setEditLoading(true);
    setProposedContent("");
    setDiffPreview([]);

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/edit/propose", {
        path: selectedFile,
        instruction: editInstruction,
      });

      const proposed = res.data.proposed_content;

      setProposedContent(proposed);
      setDiffPreview(diffLines(fileContent, proposed));
    } catch (err) {
      console.error(err);
      alert("Failed to generate edit proposal.");
    } finally {
      setEditLoading(false);
    }
  }

  function applyProposal() {
    if (!proposedContent) return;

    setFileContent(proposedContent);

    setProposedContent("");
    setDiffPreview([]);
    setEditInstruction("");
  }

  function rejectProposal() {
    setProposedContent("");
    setDiffPreview([]);
  }

  function runTerminalCommand() {
    if (!terminalCommand.trim()) return;

    setTerminalRunning(true);

    const command = terminalCommand;

    setTerminalOutput((prev) => [
      ...prev,
      {
        type: "command",
        content: `$ ${command}`,
      },
    ]);

    setTerminalCommand("");

    const socket = new WebSocket("ws://127.0.0.1:8000/api/terminal/ws");

    terminalSocketRef.current = socket;

    socket.onopen = () => {
      socket.send(command);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (
        data.type === "stdout" ||
        data.type === "stderr" ||
        data.type === "status" ||
        data.type === "error"
      ) {
        setTerminalOutput((prev) => [
          ...prev,
          {
            type: data.type,
            content: data.content,
          },
        ]);
      }

      if (data.type === "done") {
        setTerminalRunning(false);

        setTerminalOutput((prev) => [
          ...prev,
          {
            type: "done",
            content: `Process exited with code ${data.exit_code}`,
          },
        ]);

        socket.close();
      }
    };

    socket.onerror = () => {
      setTerminalRunning(false);

      setTerminalOutput((prev) => [
        ...prev,
        {
          type: "error",
          content: "Terminal connection error.",
        },
      ]);
    };
  }

  function sendMessage() {
    if (!input.trim()) return;

    const userText = input;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userText,
        traces: [],
      },
      {
        role: "assistant",
        content: "",
        traces: [],
      },
    ]);

    setInput("");
    setLoading(true);

    const socket = new WebSocket("ws://127.0.0.1:8000/api/ws/chat");

    socket.onopen = () => {
      socket.send(userText);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "token") {
        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;

          updated[lastIndex] = {
            ...updated[lastIndex],
            content: updated[lastIndex].content + data.content,
          };

          return updated;
        });
      }

      if (data.type === "traces") {
        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;

          updated[lastIndex] = {
            ...updated[lastIndex],
            traces: data.content,
          };

          return updated;
        });
      }

      if (data.type === "done") {
        setLoading(false);
        socket.close();
      }
    };

    socket.onerror = () => {
      setLoading(false);
    };
  }

  function renderTerminal() {
    return (
      <div className="terminal-panel">
        <div className="terminal-header">
          <div className="terminal-title">
            <Terminal size={16} />
            Runtime Terminal
          </div>

          {terminalRunning && <div className="terminal-running">Running...</div>}
        </div>

        <div className="terminal-output">
          {terminalOutput.map((entry, index) => (
            <div key={index} className={`terminal-line terminal-${entry.type}`}>
              {entry.content}
            </div>
          ))}
        </div>

        <div className="terminal-input-row">
          <input
            value={terminalCommand}
            onChange={(e) => setTerminalCommand(e.target.value)}
            placeholder="Run shell command..."
            onKeyDown={(e) => e.key === "Enter" && runTerminalCommand()}
          />

          <button className="terminal-run-button" onClick={runTerminalCommand}>
            <Play size={16} />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>Atlas Agent</h1>
        <p>Local AI runtime</p>

        <div className="tools">
          <div className="explorer-header">
            <h3>Project Files</h3>

            {currentPath !== "." && (
              <button className="back-button" onClick={goBackDirectory}>
                <ArrowLeft size={16} />
              </button>
            )}
          </div>

          <div className="current-path">{currentPath}</div>

          {files.map((file) => (
            <div
              key={file.path}
              className="file-item"
              onClick={() => {
                if (file.type === "file") {
                  openFile(file.path);
                } else {
                  loadFiles(file.path);
                }
              }}
            >
              {file.type === "directory" ? (
                <Folder size={16} />
              ) : (
                <FileText size={16} />
              )}

              <span>{file.name}</span>
            </div>
          ))}
        </div>
      </aside>

      <main className="main">
        <div className="top-panel">
          <div className="chat">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                <div className="message-header">
                  {msg.role === "assistant" ? <Bot size={18} /> : <User size={18} />}
                  <strong>{msg.role === "assistant" ? "Atlas" : "You"}</strong>
                </div>

                <pre>{msg.content}</pre>

                {msg.traces?.length > 0 && (
                  <div className="traces">
                    <div className="trace-title">
                      <Activity size={16} />
                      Execution Trace
                    </div>

                    {msg.traces.map((trace, i) => (
                      <div className="trace" key={i}>
                        <p>
                          <strong>Step:</strong> {trace.step}
                        </p>

                        <p>
                          <strong>Action:</strong> {trace.action}
                        </p>

                        {trace.tool_name && (
                          <p>
                            <strong>Tool:</strong> {trace.tool_name}
                          </p>
                        )}

                        <p>
                          <strong>Success:</strong> {String(trace.success)}
                        </p>

                        {trace.output_preview && (
                          <pre className="trace-output">{trace.output_preview}</pre>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {loading && <div className="loading">Atlas is thinking...</div>}
          </div>

          <div className="right-panel">
            {editorOpen ? (
              <div className="editor">
                <div className="editor-header">
                  <span>{selectedFile || "No file selected"}</span>

                  <div className="editor-actions">
                    {selectedFile && (
                      <button className="save-button" onClick={saveFile}>
                        Save
                      </button>
                    )}

                    <button
                      className="minimize-button"
                      onClick={() => setEditorOpen(false)}
                    >
                      Minimize
                    </button>
                  </div>
                </div>

                <textarea
                  className="editor-content"
                  value={fileContent}
                  onChange={(e) => setFileContent(e.target.value)}
                  placeholder="Select a file to view or edit..."
                />

                {selectedFile && (
                  <div className="ai-edit-panel">
                    <div className="ai-edit-title">
                      <Sparkles size={16} />
                      AI Edit Proposal
                    </div>

                    <textarea
                      className="edit-instruction"
                      value={editInstruction}
                      onChange={(e) => setEditInstruction(e.target.value)}
                      placeholder="Example: Add comments, refactor this file..."
                    />

                    <button
                      className="propose-button"
                      onClick={proposeEdit}
                      disabled={editLoading}
                    >
                      {editLoading ? "Generating..." : "Propose Edit"}
                    </button>

                    {diffPreview.length > 0 && (
                      <div className="proposal-box">
                        <div className="proposal-header">
                          <span>Git-Style Diff Preview</span>

                          <div className="proposal-actions">
                            <button className="apply-button" onClick={applyProposal}>
                              <Check size={15} />
                              Apply
                            </button>

                            <button className="reject-button" onClick={rejectProposal}>
                              <X size={15} />
                              Reject
                            </button>
                          </div>
                        </div>

                        <pre className="diff-content">
                          {diffPreview.map((part, index) => {
                            const className = part.added
                              ? "diff-added"
                              : part.removed
                              ? "diff-removed"
                              : "diff-normal";

                            const prefix = part.added ? "+ " : part.removed ? "- " : "  ";

                            return (
                              <span key={index} className={className}>
                                {part.value
                                  .split("\n")
                                  .filter(
                                    (line, i, arr) =>
                                      !(i === arr.length - 1 && line === "")
                                  )
                                  .map((line, lineIndex) => (
                                    <span key={lineIndex}>
                                      {prefix}
                                      {line}
                                      {"\n"}
                                    </span>
                                  ))}
                              </span>
                            );
                          })}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <button
                className="open-editor-button"
                onClick={() => setEditorOpen(true)}
              >
                Open Editor
              </button>
            )}

            {renderTerminal()}
          </div>
        </div>

        <div className="input-bar">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Atlas something..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />

          <button onClick={sendMessage}>
            <Send size={18} />
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;