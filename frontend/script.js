const API = "http://127.0.0.1:8000";

let currentPage = "dashboard";
let currentEnvironment = "AUTOMOTIVE";
let selectedFailure = "";

let nodesCache = [];
let eventsCache = [];


const NODE_PROFILES = {

    "Battery": [
        "Voltage",
        "Temperature",
        "Charge / Power"
    ],

    "Engine": [
        "Temperature",
        "Oil / Fluid Level",
        "Vibration"
    ],

    "Brake": [
        "Brake Temperature",
        "Hydraulic Pressure",
        "Pad Health"
    ],

    "Transmission": [
        "Transmission Temperature",
        "Fluid Level",
        "Gear State"
    ],

    "ECU": [
        "Temperature",
        "Signal Health",
        "Sensor Health"
    ],

    "Lighting": [
        "Voltage",
        "Lamp Health",
        "Control Signal"
    ],

    "Infotainment": [
        "Temperature",
        "Network Signal",
        "Display Health"
    ],

    "Cooling System": [
        "Coolant Temperature",
        "Coolant Level",
        "Fan State"
    ],

    "Steering": [
        "Hydraulic Pressure",
        "Motor Health",
        "Control Signal"
    ],

    "Power Supply": [
        "Voltage",
        "Temperature",
        "Power Stability"
    ],

    "CPU": [
        "Temperature",
        "Processor Load",
        "Core Health"
    ],

    "RAM": [
        "Memory Usage",
        "Temperature",
        "Memory Health"
    ],

    "GPU": [
        "Temperature",
        "GPU Load",
        "VRAM Health"
    ],

    "Storage": [
        "Drive Temperature",
        "Read Health",
        "Write Health"
    ],

    "Network Adapter": [
        "Signal Strength",
        "Packet Health",
        "Link State"
    ],

    "Operating System": [
        "Boot Health",
        "Service Health",
        "System State"
    ],

    "Motherboard": [
        "Temperature",
        "Voltage",
        "Bus Health"
    ],

    "Flight Computer": [
        "Temperature",
        "System Health",
        "Sensor Health"
    ],

    "Navigation": [
        "Signal Quality",
        "Position Accuracy",
        "Sensor Health"
    ],

    "Radar": [
        "Signal Quality",
        "Detection Health",
        "Sensor Health"
    ],

    "Hydraulic System": [
        "Hydraulic Pressure",
        "Fluid Level",
        "Pump Health"
    ],

    "Landing Gear": [
        "Hydraulic Pressure",
        "Lock State",
        "Position Sensor"
    ],

    "Communication": [
        "Signal Strength",
        "Radio Health",
        "Link State"
    ],

    "Fuel System": [
        "Fuel Pressure",
        "Fuel Level",
        "Pump Health"
    ]

};


const NODE_ICONS = {

    "Battery": "🔋",
    "Engine": "⚙️",
    "Brake": "🛑",
    "Transmission": "🔧",
    "ECU": "🧠",
    "Lighting": "💡",
    "Infotainment": "🎵",
    "Cooling System": "❄️",
    "Steering": "🛞",

    "Power Supply": "⚡",
    "CPU": "🖥️",
    "RAM": "💾",
    "GPU": "🎮",
    "Storage": "💿",
    "Network Adapter": "🌐",
    "Operating System": "💻",
    "Motherboard": "🔲",

    "Flight Computer": "🧠",
    "Navigation": "🧭",
    "Radar": "📡",
    "Hydraulic System": "💧",
    "Landing Gear": "🛬",
    "Communication": "📻",
    "Fuel System": "⛽"

};


function escapeHTML(value) {

    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


function statusClass(status) {

    return String(status || "")
        .toLowerCase()
        .replaceAll(" ", "-");

}


function getNodeProfile(nodeType) {

    return NODE_PROFILES[nodeType] || [
        "Health",
        "Status",
        "Failure State"
    ];

}


function getNodeIcon(nodeType) {

    return NODE_ICONS[nodeType] || "🔧";

}


/* ============================================================
   API
============================================================ */

async function api(endpoint, options = {}) {

    const response = await fetch(
        `${API}${endpoint}`,
        {
            headers: {
                "Content-Type": "application/json"
            },
            ...options
        }
    );

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {

        throw new Error(
            data?.message || `HTTP ${response.status}`
        );

    }

    return data;

}


/* ============================================================
   TOAST
============================================================ */

function showToast(message, type = "success") {

    const container =
        document.getElementById("toast-container");

    const toast =
        document.createElement("div");

    toast.className =
        `toast ${type}`;

    toast.textContent =
        message;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add("show");
    });

    setTimeout(() => {

        toast.classList.remove("show");

        setTimeout(() => {
            toast.remove();
        }, 220);

    }, 2800);

}


/* ============================================================
   CONFIRMATION MODAL
============================================================ */

function showConfirm(message, callback) {

    let modal =
        document.getElementById("confirm-modal");

    if (!modal) {

        modal =
            document.createElement("div");

        modal.id =
            "confirm-modal";

        modal.className =
            "modal";

        modal.innerHTML = `

            <div
                class="modal-content"
                style="max-width:500px"
            >

                <h2>
                    Confirm Action
                </h2>

                <p id="confirm-message"></p>

                <div class="modal-actions">

                    <button
                        id="confirm-cancel"
                        class="secondary-button"
                    >
                        Cancel
                    </button>

                    <button
                        id="confirm-ok"
                        class="danger-button"
                    >
                        Confirm
                    </button>

                </div>

            </div>

        `;

        document.body.appendChild(modal);

    }


    modal
        .querySelector("#confirm-message")
        .textContent = message;

    modal.classList.add("active");


    modal
        .querySelector("#confirm-cancel")
        .onclick = () => {

            modal.classList.remove("active");

        };


    modal
        .querySelector("#confirm-ok")
        .onclick = async () => {

            modal.classList.remove("active");

            await callback();

        };

}


/* ============================================================
   ENVIRONMENT
============================================================ */

async function setupEnvironmentSelector() {

    let selector =
        document.getElementById(
            "environment-selector"
        );

    if (!selector) {

        selector =
            document.createElement("select");

        selector.id =
            "environment-selector";

        selector.className =
            "environment-selector";

        document
            .querySelector(".topbar")
            .appendChild(selector);

    }


    try {

        const environments =
            await api("/environments");

        selector.innerHTML =
            environments
                .map(environment => {

                    const icon =
                        environment === "AUTOMOTIVE"
                            ? "🚗"
                            : environment === "PC"
                                ? "🖥️"
                                : "✈️";

                    return `
                        <option value="${environment}">
                            ${icon} ${environment}
                        </option>
                    `;

                })
                .join("");


        selector.value =
            currentEnvironment;


        selector.onchange =
            async () => {

                currentEnvironment =
                    selector.value;

                selectedFailure = "";

                await refreshAll();

                showToast(
                    `${currentEnvironment} environment selected`
                );

            };

    }

    catch (error) {

        console.error(error);

        showToast(
            "Could not load environments",
            "error"
        );

    }

}


/* ============================================================
   NAVIGATION
============================================================ */

function setupNavigation() {

    document
        .querySelectorAll("[data-page]")
        .forEach(button => {

            button.addEventListener(
                "click",
                async () => {

                    currentPage =
                        button.dataset.page;

                    document
                        .querySelectorAll("[data-page]")
                        .forEach(item =>
                            item.classList.remove("active")
                        );

                    button.classList.add("active");


                    document
                        .querySelectorAll(".page")
                        .forEach(page =>
                            page.classList.remove(
                                "active-page"
                            )
                        );


                    const target =
                        document.getElementById(
                            `${currentPage}-page`
                        );

                    if (target) {
                        target.classList.add(
                            "active-page"
                        );
                    }


                    await loadPage(
                        currentPage
                    );

                }
            );

        });

}


async function loadPage(page) {

    try {

        if (page === "dashboard") {
            await loadDashboard();
        }

        else if (page === "nodes") {
            await loadNodes();
        }

        else if (page === "testing") {
            await loadTesting();
        }

        else if (page === "failures") {
            await loadFailures();
        }

        else if (page === "logs") {
            await loadLogs();
        }

        else if (page === "history") {
            await loadHistory();
        }

    }

    catch (error) {

        console.error(error);

        showToast(
            error.message ||
            "Could not load page",
            "error"
        );

    }

}


/* ============================================================
   DASHBOARD
============================================================ */

async function loadDashboard() {

    const data =
        await api("/dashboard");

    nodesCache =
        data.nodes || [];

    eventsCache =
        data.events || [];


    const environmentNodes =
        nodesCache.filter(
            node =>
                node.environment ===
                currentEnvironment
        );


    const environmentFailures =
        (data.failures || [])
            .filter(failure => {

                const node =
                    nodesCache.find(
                        n =>
                            n.node_id ===
                            failure.node_id
                    );

                return (
                    node &&
                    node.environment ===
                    currentEnvironment &&
                    failure.active
                );

            });


    document.getElementById(
        "node-count"
    ).textContent =
        environmentNodes.length;


    document.getElementById(
        "test-count"
    ).textContent =
        (data.results || [])
            .filter(result =>
                environmentNodes.some(
                    node =>
                        result.test_name
                            .startsWith(
                                node.node_type
                            )
                )
            )
            .length;


    document.getElementById(
        "failure-count"
    ).textContent =
        environmentFailures.length;


    const health =
        environmentNodes.length
            ? Math.round(
                environmentNodes.reduce(
                    (sum, node) =>
                        sum +
                        Number(
                            node.health ?? 0
                        ),
                    0
                ) /
                environmentNodes.length
            )
            : 0;


    document.getElementById(
        "health-value"
    ).textContent =
        `${health}%`;


    renderDashboardNodes(
        environmentNodes
    );


    renderRecentActivity(
        eventsCache.slice(0, 8)
    );


    populateFailureNodeSelect(
        environmentNodes
    );

}


function renderDashboardNodes(nodes) {

    const container =
        document.getElementById(
            "dashboard-nodes"
        );


    if (!nodes.length) {

        container.innerHTML = `

            <div class="empty-state">
                No nodes in
                ${escapeHTML(currentEnvironment)}.
            </div>

        `;

        return;

    }


    container.innerHTML =
        nodes
            .slice(0, 8)
            .map(node => `

                <div
                    class="mini-node"
                    data-node-id="${escapeHTML(
                        node.node_id
                    )}"
                >

                    <div>

                        <strong>
                            ${getNodeIcon(
                                node.node_type
                            )}
                            ${escapeHTML(
                                node.node_type
                            )}
                        </strong>

                        <small>
                            ${escapeHTML(
                                node.node_id
                            )}
                        </small>

                    </div>


                    <span
                        class="status-badge status-${statusClass(
                            node.status
                        )}"
                    >
                        ${escapeHTML(
                            node.status
                        )}
                    </span>

                </div>

            `)
            .join("");


    container
        .querySelectorAll(".mini-node")
        .forEach(item => {

            item.onclick =
                () =>
                    openNodeDetails(
                        item.dataset.nodeId
                    );

        });

}


function renderRecentActivity(events) {

    const container =
        document.getElementById(
            "recent-activity"
        );


    if (!events.length) {

        container.innerHTML = `

            <div class="empty-state">
                No recent activity.
            </div>

        `;

        return;

    }


    container.innerHTML =
        events
            .map(event => `

                <div class="activity-item">

                    <strong>
                        ${escapeHTML(
                            event.event_type
                        )}
                    </strong>

                    <p>
                        ${escapeHTML(
                            event.description
                        )}
                    </p>

                    <span>
                        ${escapeHTML(
                            event.event_time
                        )}
                    </span>

                </div>

            `)
            .join("");

}


/* ============================================================
   NODES
============================================================ */

async function loadNodes() {

    nodesCache =
        await api("/nodes");


    renderNodes(
        nodesCache.filter(
            node =>
                node.environment ===
                currentEnvironment
        )
    );

}


function renderNodes(nodes) {

    const container =
        document.getElementById(
            "nodes-grid"
        );


    if (!nodes.length) {

        container.innerHTML = `

            <div class="panel empty-state">
                No
                ${escapeHTML(
                    currentEnvironment
                )}
                nodes found.
            </div>

        `;

        return;

    }


    container.innerHTML =
        nodes
            .map(node => {

                const profile =
                    getNodeProfile(
                        node.node_type
                    );


                return `

                    <div class="node-card">

                        <div class="node-card-header">

                            <div class="node-title-area">

                                <div class="node-visual">
                                    ${getNodeIcon(
                                        node.node_type
                                    )}
                                </div>

                                <div>

                                    <h3>
                                        ${escapeHTML(
                                            node.node_type
                                        )}
                                    </h3>

                                    <span class="node-id">
                                        ${escapeHTML(
                                            node.node_id
                                        )}
                                    </span>

                                </div>

                            </div>


                            <span
                                class="status-badge status-${statusClass(
                                    node.status
                                )}"
                            >
                                ${escapeHTML(
                                    node.status
                                )}
                            </span>

                        </div>


                        <div class="node-metrics">

                            <div>
                                <span>Health</span>
                                <strong>
                                    ${Number(
                                        node.health ?? 0
                                    )}%
                                </strong>
                            </div>

                            <div>
                                <span>CPU</span>
                                <strong>
                                    ${Number(
                                        node.cpu_usage ?? 0
                                    )}%
                                </strong>
                            </div>

                            <div>
                                <span>Memory</span>
                                <strong>
                                    ${Number(
                                        node.memory_usage ?? 0
                                    )}%
                                </strong>
                            </div>

                        </div>


                        <div class="node-profile">

                            <span>
                                MONITORED
                            </span>

                            <p>
                                ${profile
                                    .map(
                                        escapeHTML
                                    )
                                    .join(" • ")}
                            </p>

                        </div>


                        <div class="node-actions">

                            <button
                                class="primary-button"
                                data-detail="${escapeHTML(
                                    node.node_id
                                )}"
                            >
                                Details
                            </button>

                            <button
                                class="danger-button"
                                data-delete="${escapeHTML(
                                    node.node_id
                                )}"
                            >
                                Delete
                            </button>

                        </div>

                    </div>

                `;

            })
            .join("");


    container
        .querySelectorAll("[data-detail]")
        .forEach(button => {

            button.onclick =
                () =>
                    openNodeDetails(
                        button.dataset.detail
                    );

        });


    container
        .querySelectorAll("[data-delete]")
        .forEach(button => {

            button.onclick =
                () =>
                    deleteNode(
                        button.dataset.delete
                    );

        });

}


/* ============================================================
   NODE DETAILS
============================================================ */

async function openNodeDetails(nodeId) {

    try {

        const response =
            await api(
                `/nodes/${encodeURIComponent(
                    nodeId
                )}`
            );


        const node =
            response.node ||
            response;


        const failures =
            (
                response.failures ||
                await api(
                    `/nodes/${encodeURIComponent(
                        nodeId
                    )}/failures`
                )
            )
            .filter(
                failure =>
                    failure.active
            );


        let diagnosis =
            "No problem detected.";

        let recommendedFix =
            "No action required. Component is operating normally.";


        if (failures.length) {

            diagnosis =
                `Active failure: ${failures
                    .map(
                        failure =>
                            failure.failure_type
                    )
                    .join(", ")}`;

            recommendedFix =
                "Remove the active failure or recover the node.";

        }

        else if (node.status !== "ONLINE") {

            diagnosis =
                "Component is offline and has no active injected failure.";

            recommendedFix =
                "Check dependencies or power ON the component.";

        }

        else if (
            Number(node.health) < 50
        ) {

            diagnosis =
                `Component health is critically low at ${node.health}%.`;

            recommendedFix =
                "Recover the component and investigate the cause.";

        }


        let modal =
            document.getElementById(
                "node-details-modal"
            );


        if (!modal) {

            modal =
                document.createElement(
                    "div"
                );

            modal.id =
                "node-details-modal";

            modal.className =
                "modal";

            document.body.appendChild(
                modal
            );

        }


        modal.innerHTML = `

            <div class="modal-content large-modal">

                <div class="modal-header">

                    <div class="node-title-area">

                        <div class="node-visual">
                            ${getNodeIcon(
                                node.node_type
                            )}
                        </div>

                        <div>

                            <span class="eyebrow">
                                ${escapeHTML(
                                    node.environment
                                )}
                            </span>

                            <h2>
                                ${escapeHTML(
                                    node.node_type
                                )}
                            </h2>

                            <p>
                                ${escapeHTML(
                                    node.node_id
                                )}
                            </p>

                        </div>

                    </div>


                    <button
                        class="modal-close"
                        id="details-close"
                    >
                        ×
                    </button>

                </div>


                <div class="detail-grid">

                    <div class="detail-box">
                        <span>Status</span>
                        <strong>
                            ${escapeHTML(
                                node.status
                            )}
                        </strong>
                    </div>

                    <div class="detail-box">
                        <span>Health</span>
                        <strong>
                            ${Number(
                                node.health ?? 0
                            )}%
                        </strong>
                    </div>

                    <div class="detail-box">
                        <span>CPU</span>
                        <strong>
                            ${Number(
                                node.cpu_usage ?? 0
                            )}%
                        </strong>
                    </div>

                    <div class="detail-box">
                        <span>Memory</span>
                        <strong>
                            ${Number(
                                node.memory_usage ?? 0
                            )}%
                        </strong>
                    </div>

                    <div class="detail-box">
                        <span>Priority</span>
                        <strong>
                            ${escapeHTML(
                                node.priority
                            )}
                        </strong>
                    </div>

                    <div class="detail-box">
                        <span>Tracked</span>
                        <strong>
                            ${escapeHTML(
                                getNodeProfile(
                                    node.node_type
                                )[0]
                            )}
                        </strong>
                    </div>

                </div>


                <h3>
                    Active Failures
                </h3>


                <div class="failure-list">

                    ${
                        failures.length

                        ?

                        failures
                            .map(
                                failure => `

                                    <div
                                        class="failure-item"
                                    >

                                        <span>
                                            ${escapeHTML(
                                                failure.failure_type
                                            )}
                                        </span>

                                        <button
                                            class="danger-button"
                                            data-remove="${failure.id}"
                                        >
                                            Remove
                                        </button>

                                    </div>

                                `
                            )
                            .join("")

                        :

                        `
                            <div class="empty-state">
                                No active failures.
                            </div>
                        `
                    }

                </div>


                <h3>
                    Diagnosis
                </h3>


                <div class="diagnosis-box">

                    <div>

                        <span>
                            Detected Problem
                        </span>

                        <strong>
                            ${escapeHTML(
                                diagnosis
                            )}
                        </strong>

                    </div>


                    <div>

                        <span>
                            Recommended Fix
                        </span>

                        <strong>
                            ${escapeHTML(
                                recommendedFix
                            )}
                        </strong>

                    </div>

                </div>


                <div class="modal-actions">

                    <button
                        class="secondary-button"
                        id="detail-power"
                    >
                        ${
                            node.status === "ONLINE"
                                ? "Power OFF"
                                : "Power ON"
                        }
                    </button>


                    <button
                        class="primary-button"
                        id="detail-recover"
                    >
                        Recover Node
                    </button>

                </div>

            </div>

        `;


        modal.classList.add(
            "active"
        );


        modal.onclick =
            event => {

                if (
                    event.target ===
                    modal
                ) {
                    modal.classList.remove(
                        "active"
                    );
                }

            };


        modal
            .querySelector("#details-close")
            .onclick = () => {

                modal.classList.remove(
                    "active"
                );

            };


        modal
            .querySelector("#detail-power")
            .onclick = async () => {

                await powerNode(
                    node.node_id,
                    node.status === "ONLINE"
                        ? "OFF"
                        : "ON"
                );

                modal.classList.remove(
                    "active"
                );

            };


        modal
            .querySelector("#detail-recover")
            .onclick = async () => {

                await recoverNode(
                    node.node_id
                );

                modal.classList.remove(
                    "active"
                );

            };


        modal
            .querySelectorAll(
                "[data-remove]"
            )
            .forEach(button => {

                button.onclick =
                    async () => {

                        await removeFailure(
                            Number(
                                button.dataset.remove
                            )
                        );

                        modal.classList.remove(
                            "active"
                        );

                    };

            });

    }

    catch (error) {

        console.error(error);

        showToast(
            error.message ||
            "Could not load node details",
            "error"
        );

    }

}


/* ============================================================
   POWER
============================================================ */

async function powerNode(
    nodeId,
    action
) {

    try {

        const data =
            await api(
                `/nodes/${encodeURIComponent(
                    nodeId
                )}/power`,
                {
                    method:"POST",
                    body:JSON.stringify({
                        action
                    })
                }
            );


        if (!data.success) {
            throw new Error(
                data.message
            );
        }


        showToast(
            data.message
        );


        await refreshAll();

    }

    catch (error) {

        showToast(
            error.message ||
            "Power operation failed",
            "error"
        );

    }

}


async function powerAllNodes(
    action
) {

    showConfirm(
        `${
            action === "ON"
                ? "POWER ON"
                : "POWER OFF"
        } all ${currentEnvironment} nodes?`,

        async () => {

            try {

                const data =
                    await api(
                        "/environment/power",
                        {
                            method:"POST",
                            body:JSON.stringify({
                                environment:
                                    currentEnvironment,
                                action
                            })
                        }
                    );


                if (!data.success) {
                    throw new Error(
                        data.message
                    );
                }


                showToast(
                    data.message
                );


                await refreshAll();

            }

            catch (error) {

                showToast(
                    error.message ||
                    "System power operation failed",
                    "error"
                );

            }

        }
    );

}


/* ============================================================
   RECOVERY
============================================================ */

async function recoverNode(
    nodeId
) {

    showConfirm(
        "Recover this node and remove its active failures?",

        async () => {

            try {

                const data =
                    await api(
                        `/nodes/${encodeURIComponent(
                            nodeId
                        )}/recover`,
                        {
                            method:"POST"
                        }
                    );


                if (!data.success) {
                    throw new Error(
                        data.message
                    );
                }


                showToast(
                    data.message
                );


                await refreshAll();

            }

            catch (error) {

                showToast(
                    error.message ||
                    "Recovery failed",
                    "error"
                );

            }

        }
    );

}


/* ============================================================
   DELETE NODE
============================================================ */

async function deleteNode(
    nodeId
) {

    showConfirm(
        `Delete node ${nodeId}?`,

        async () => {

            try {

                const data =
                    await api(
                        `/nodes/${encodeURIComponent(
                            nodeId
                        )}`,
                        {
                            method:"DELETE"
                        }
                    );


                if (!data.success) {
                    throw new Error(
                        data.message
                    );
                }


                showToast(
                    "Node deleted"
                );


                await refreshAll();

            }

            catch (error) {

                showToast(
                    error.message ||
                    "Could not delete node",
                    "error"
                );

            }

        }
    );

}


/* ============================================================
   ADD NODE
============================================================ */

async function openAddNodeModal() {

    const modal =
        document.getElementById(
            "node-modal"
        );

    const typeSelect =
        document.getElementById(
            "new-node-type"
        );


    try {

        const types =
            await api(
                `/environments/${encodeURIComponent(
                    currentEnvironment
                )}`
            );


        typeSelect.innerHTML =
            types
                .map(
                    type => `

                        <option
                            value="${escapeHTML(
                                type
                            )}"
                        >
                            ${getNodeIcon(
                                type
                            )}
                            ${escapeHTML(
                                type
                            )}
                        </option>

                    `
                )
                .join("");


        document
            .querySelector(
                "#node-modal .modal-header p"
            )
            .textContent =
            `Create a node for ${currentEnvironment}.`;


        modal.classList.add(
            "active"
        );


        document
            .getElementById(
                "new-node-id"
            )
            .focus();

    }

    catch (error) {

        console.error(error);

        showToast(
            "Could not load node types",
            "error"
        );

    }

}


function closeAddNodeModal() {

    document
        .getElementById(
            "node-modal"
        )
        ?.classList.remove(
            "active"
        );

}


async function createNode() {

    const id =
        document
            .getElementById(
                "new-node-id"
            )
            .value
            .trim();

    const type =
        document
            .getElementById(
                "new-node-type"
            )
            .value;


    if (!id) {

        showToast(
            "Enter a node ID",
            "error"
        );

        return;

    }


    if (!type) {

        showToast(
            "Select a node type",
            "error"
        );

        return;

    }


    try {

        const data =
            await api(
                "/nodes",
                {
                    method:"POST",

                    body:JSON.stringify({
                        node_id:id,
                        node_type:type,
                        environment:
                            currentEnvironment
                    })
                }
            );


        if (!data.success) {

            throw new Error(
                data.message
            );

        }


        showToast(
            `${type} created successfully`
        );


        document
            .getElementById(
                "new-node-id"
            )
            .value = "";


        closeAddNodeModal();


        await refreshAll();

    }

    catch (error) {

        showToast(
            error.message ||
            "Could not create node",
            "error"
        );

    }

}


/* ============================================================
   FAILURES
============================================================ */

function populateFailureNodeSelect(
    nodes
) {

    const select =
        document.getElementById(
            "failure-node"
        );


    if (!nodes.length) {

        select.innerHTML = `
            <option value="">
                No nodes in this environment
            </option>
        `;

        renderDynamicFailureOptions([]);

        return;

    }


    select.innerHTML =
        nodes
            .map(
                node => `

                    <option
                        value="${escapeHTML(
                            node.node_id
                        )}"
                    >
                        ${getNodeIcon(
                            node.node_type
                        )}
                        ${escapeHTML(
                            node.node_type
                        )}
                        (${escapeHTML(
                            node.node_id
                        )})
                    </option>

                `
            )
            .join("");


    loadFailureOptionsForNode(
        nodes[0].node_id
    );

}


async function loadFailureOptionsForNode(
    nodeId
) {

    const node =
        nodesCache.find(
            n =>
                n.node_id ===
                nodeId
        );


    if (!node) {

        renderDynamicFailureOptions([]);

        return;

    }


    try {

        const data =
            await api(
                `/node-types/${encodeURIComponent(
                    currentEnvironment
                )}/${encodeURIComponent(
                    node.node_type
                )}/failures`
            );


        renderDynamicFailureOptions(
            data.failures || []
        );

    }

    catch (error) {

        console.error(error);

        renderDynamicFailureOptions([]);

    }

}


function renderDynamicFailureOptions(
    failures
) {

    const container =
        document.querySelector(
            ".failure-options"
        );


    if (!container) {
        return;
    }


    if (!failures.length) {

        container.innerHTML = `
            <div class="empty-state">
                No failures available for this component.
            </div>
        `;

        selectedFailure = "";

        return;

    }


    selectedFailure =
        failures[0];


    container.innerHTML =
        failures
            .map(
                (failure, index) => `

                    <button
                        type="button"
                        class="failure-option ${
                            index === 0
                                ? "selected"
                                : ""
                        }"
                        data-failure="${escapeHTML(
                            failure
                        )}"
                    >
                        ${failure.replaceAll(
                            "_",
                            " "
                        )}
                    </button>

                `
            )
            .join("");


    container
        .querySelectorAll(
            ".failure-option"
        )
        .forEach(button => {

            button.onclick =
                () => {

                    container
                        .querySelectorAll(
                            ".failure-option"
                        )
                        .forEach(item =>
                            item.classList.remove(
                                "selected"
                            )
                        );


                    button.classList.add(
                        "selected"
                    );


                    selectedFailure =
                        button.dataset.failure;

                };

        });

}


async function loadFailures() {

    const [
        failures,
        nodes
    ] =
        await Promise.all([
            api("/failures"),
            api("/nodes")
        ]);


    nodesCache =
        nodes;


    const environmentNodes =
        nodes.filter(
            node =>
                node.environment ===
                currentEnvironment
        );


    populateFailureNodeSelect(
        environmentNodes
    );


    renderFailures(
        failures.filter(
            failure =>
                environmentNodes.some(
                    node =>
                        node.node_id ===
                        failure.node_id
                )
        )
    );

}


function renderFailures(
    failures
) {

    const container =
        document.getElementById(
            "failures-table"
        );


    if (!failures.length) {

        container.innerHTML = `

            <tr>
                <td
                    colspan="4"
                    class="empty-state"
                >
                    No failures found.
                </td>
            </tr>

        `;

        return;

    }


    container.innerHTML =
        failures
            .map(
                failure => `

                    <tr>

                        <td>
                            ${escapeHTML(
                                failure.node_id
                            )}
                        </td>

                        <td>
                            ${escapeHTML(
                                failure.failure_type
                            )}
                        </td>

                        <td>

                            ${
                                failure.active

                                ?

                                `
                                    <span
                                        class="status-badge status-warning"
                                    >
                                        ACTIVE
                                    </span>
                                `

                                :

                                "RESOLVED"
                            }

                        </td>

                        <td>

                            ${
                                failure.active

                                ?

                                `
                                    <button
                                        class="danger-button"
                                        data-remove-failure="${failure.id}"
                                    >
                                        Remove
                                    </button>
                                `

                                :

                                "—"
                            }

                        </td>

                    </tr>

                `
            )
            .join("");


    container
        .querySelectorAll(
            "[data-remove-failure]"
        )
        .forEach(button => {

            button.onclick =
                () =>
                    removeFailure(
                        Number(
                            button.dataset
                                .removeFailure
                        )
                    );

        });

}


async function injectFailure() {

    const nodeId =
        document
            .getElementById(
                "failure-node"
            )
            .value;


    if (!nodeId) {

        showToast(
            "Select a node",
            "error"
        );

        return;

    }


    if (!selectedFailure) {

        showToast(
            "Select a failure",
            "error"
        );

        return;

    }


    try {

        const data =
            await api(
                "/failures",
                {
                    method:"POST",

                    body:JSON.stringify({
                        node_id:nodeId,
                        failure_type:
                            selectedFailure
                    })
                }
            );


        if (!data.success) {

            throw new Error(
                data.message
            );

        }


        showToast(
            `${selectedFailure.replaceAll(
                "_",
                " "
            )} injected`
        );


        await refreshAll();

    }

    catch (error) {

        showToast(
            error.message ||
            "Failure injection failed",
            "error"
        );

    }

}


async function removeFailure(
    failureId
) {

    try {

        const data =
            await api(
                `/failures/${failureId}`,
                {
                    method:"DELETE"
                }
            );


        if (!data.success) {

            throw new Error(
                data.message
            );

        }


        showToast(
            "Failure removed"
        );


        await refreshAll();

    }

    catch (error) {

        showToast(
            error.message ||
            "Could not remove failure",
            "error"
        );

    }

}


/* ============================================================
   TESTING
============================================================ */

async function loadTesting() {

    const [
        tests,
        results
    ] =
        await Promise.all([
            api("/tests"),
            api("/results")
        ]);


    renderTests(
        tests
    );

    renderResults(
        results
    );

}


function renderTests(
    tests
) {

    const container =
        document.getElementById(
            "tests-grid"
        );


    const names =
        [
            ...new Set(
                tests.map(
                    test =>
                        test.test_name
                )
            )
        ]
        .slice(0, 12);


    if (!names.length) {

        container.innerHTML = `
            <div class="panel empty-state">
                No tests have been executed yet.
            </div>
        `;

        return;

    }


    container.innerHTML =
        names
            .map(
                test => `

                    <div class="test-card">

                        <div class="test-icon">
                            ✓
                        </div>

                        <div>

                            <strong>
                                ${escapeHTML(
                                    test
                                )}
                            </strong>

                            <span>
                                Stored test
                            </span>

                        </div>

                    </div>

                `
            )
            .join("");

}


function renderResults(
    results
) {

    const container =
        document.getElementById(
            "results-table"
        );


    if (!results.length) {

        container.innerHTML = `
            <tr>
                <td
                    colspan="3"
                    class="empty-state"
                >
                    No results yet.
                </td>
            </tr>
        `;

        return;

    }


    container.innerHTML =
        results
            .slice(0, 50)
            .map(
                result => `

                    <tr>

                        <td>
                            ${escapeHTML(
                                result.test_name
                            )}
                        </td>

                        <td>

                            <span
                                class="status-badge status-${statusClass(
                                    result.status
                                )}"
                            >
                                ${escapeHTML(
                                    result.status
                                )}
                            </span>

                        </td>

                        <td>
                            ${escapeHTML(
                                result.message
                            )}
                        </td>

                    </tr>

                `
            )
            .join("");

}


async function runTests(
    button
) {

    button.disabled =
        true;

    button.classList.add(
        "loading"
    );


    const progress =
        document.getElementById(
            "test-progress"
        );


    progress.style.width =
        "10%";


    try {

        setTimeout(
            () => {
                progress.style.width =
                    "45%";
            },
            200
        );


        setTimeout(
            () => {
                progress.style.width =
                    "75%";
            },
            500
        );


        const data =
            await api(
                "/run-tests",
                {
                    method:"POST",

                    body:JSON.stringify({
                        environment:
                            currentEnvironment
                    })
                }
            );


        if (!data.success) {

            throw new Error(
                data.message
            );

        }


        progress.style.width =
            "100%";


        showToast(
            `${data.message} — ${data.passed} passed, ${data.failed} failed`
        );


        await Promise.all([
            loadDashboard(),
            loadTesting(),
            loadHistory()
        ]);

    }

    catch (error) {

        showToast(
            error.message ||
            "Failed to run tests",
            "error"
        );

    }

    finally {

        button.disabled =
            false;

        button.classList.remove(
            "loading"
        );

    }

}


/* ============================================================
   LOGS
============================================================ */

async function loadLogs() {

    const events =
        await api("/events");

    eventsCache =
        events;


    renderLogs(
        events
    );

}


function renderLogs(
    events
) {

    const container =
        document.getElementById(
            "logs-container"
        );


    if (!events.length) {

        container.innerHTML = `
            <div class="empty-state">
                No logs available.
            </div>
        `;

        return;

    }


    container.innerHTML =
        events
            .map(
                event => `

                    <div
                        class="log-entry"
                        data-type="${escapeHTML(
                            event.event_type
                        )}"
                    >

                        <div>

                            <strong>
                                ${escapeHTML(
                                    event.event_type
                                )}
                            </strong>

                            <p>
                                ${escapeHTML(
                                    event.description
                                )}
                            </p>

                        </div>

                        <time>
                            ${escapeHTML(
                                event.event_time
                            )}
                        </time>

                    </div>

                `
            )
            .join("");

}


function setupLogFilters() {

    document
        .querySelectorAll(".filter")
        .forEach(button => {

            button.onclick =
                () => {

                    document
                        .querySelectorAll(
                            ".filter"
                        )
                        .forEach(item =>
                            item.classList.remove(
                                "active"
                            )
                        );


                    button.classList.add(
                        "active"
                    );


                    const filter =
                        button.dataset.filter;


                    document
                        .querySelectorAll(
                            ".log-entry"
                        )
                        .forEach(entry => {

                            const type =
                                entry.dataset.type
                                    .toLowerCase();


                            entry.style.display =
                                filter === "all" ||
                                type.includes(
                                    filter
                                ) ||
                                (
                                    filter === "chaos" &&
                                    type.includes(
                                        "failure"
                                    )
                                )
                                    ? ""
                                    : "none";

                        });

                };

        });

}


async function clearLogs() {

    showConfirm(
        "Clear all logs?",

        async () => {

            try {

                const response =
                    await api(
                        "/events",
                        {
                            method:"DELETE"
                        }
                    );


                if (!response.success) {

                    throw new Error(
                        response.message
                    );

                }


                showToast(
                    "Logs cleared"
                );


                await loadLogs();

            }

            catch (error) {

                showToast(
                    error.message ||
                    "Could not clear logs",
                    "error"
                );

            }

        }
    );

}


/* ============================================================
   HISTORY
============================================================ */

async function loadHistory() {

    const runs =
        await api("/runs");


    renderHistory(
        runs
    );

}


function renderHistory(
    runs
) {

    const container =
        document.getElementById(
            "history-container"
        );


    if (!runs.length) {

        container.innerHTML = `
            <div class="empty-state">
                No test runs yet.
            </div>
        `;

        return;

    }


    container.innerHTML =
        runs
            .map(
                run => `

                    <div class="history-item">

                        <strong>
                            Test Run #${run.id}
                        </strong>

                        <span>
                            ${escapeHTML(
                                run.run_time
                            )}
                        </span>

                    </div>

                `
            )
            .join("");

}


async function clearHistory() {

    showConfirm(
        "Clear test history?",

        async () => {

            try {

                const response =
                    await api(
                        "/runs",
                        {
                            method:"DELETE"
                        }
                    );


                if (!response.success) {

                    throw new Error(
                        response.message
                    );

                }


                showToast(
                    "History cleared"
                );


                await loadHistory();

            }

            catch (error) {

                showToast(
                    error.message ||
                    "Could not clear history",
                    "error"
                );

            }

        }
    );

}


/* ============================================================
   SEARCH
============================================================ */

function setupSearch() {

    const search =
        document.getElementById(
            "global-search"
        );


    search.oninput =
        () => {

            const query =
                search.value
                    .trim()
                    .toLowerCase();


            document
                .querySelectorAll(
                    ".node-card, .mini-node, .test-card, .log-entry, .history-item"
                )
                .forEach(card => {

                    card.style.display =
                        !query ||
                        card.textContent
                            .toLowerCase()
                            .includes(query)
                            ? ""
                            : "none";

                });

        };

}


/* ============================================================
   SETTINGS
============================================================ */

function setupSettings() {

    const animationToggle =
        document.getElementById(
            "animation-toggle"
        );

    const darkToggle =
        document.getElementById(
            "dark-toggle"
        );

    const defaultEnvironment =
        document.getElementById(
            "default-environment"
        );


    animationToggle.onchange =
        () => {

            document.body.classList.toggle(
                "disable-animations",
                !animationToggle.checked
            );

        };


    darkToggle.onchange =
        () => {

            document.body.classList.toggle(
                "light-interface",
                !darkToggle.checked
            );

        };


    defaultEnvironment.onchange =
        () => {

            currentEnvironment =
                defaultEnvironment.value;


            const selector =
                document.getElementById(
                    "environment-selector"
                );


            if (selector) {
                selector.value =
                    currentEnvironment;
            }


            refreshAll();

        };

}


/* ============================================================
   BUTTONS
============================================================ */

function setupButtons() {

    document
        .getElementById(
            "add-node-button"
        )
        .onclick =
        openAddNodeModal;


    document
        .getElementById(
            "create-node-button"
        )
        .onclick =
        createNode;


    document
        .getElementById(
            "close-node-modal"
        )
        .onclick =
        closeAddNodeModal;


    document
        .getElementById(
            "close-node-modal-bottom"
        )
        .onclick =
        closeAddNodeModal;


    document
        .getElementById(
            "node-modal"
        )
        .onclick =
        event => {

            if (
                event.target.id ===
                "node-modal"
            ) {
                closeAddNodeModal();
            }

        };


    document
        .getElementById(
            "inject-failure-button"
        )
        .onclick =
        injectFailure;


    document
        .getElementById(
            "run-tests-button"
        )
        .onclick =
        () =>
            runTests(
                document.getElementById(
                    "run-tests-button"
                )
            );


    document
        .getElementById(
            "dashboard-run-tests"
        )
        .onclick =
        () =>
            runTests(
                document.getElementById(
                    "dashboard-run-tests"
                )
            );


    document
        .getElementById(
            "power-all-on-button"
        )
        .onclick =
        () =>
            powerAllNodes("ON");


    document
        .getElementById(
            "power-all-off-button"
        )
        .onclick =
        () =>
            powerAllNodes("OFF");


    document
        .getElementById(
            "clear-logs-button"
        )
        .onclick =
        clearLogs;


    document
        .getElementById(
            "clear-history-button"
        )
        .onclick =
        clearHistory;


    document
        .getElementById(
            "refresh-button"
        )
        .onclick =
        () =>
            refreshAll();


    document
        .getElementById(
            "failure-node"
        )
        .onchange =
        event =>
            loadFailureOptionsForNode(
                event.target.value
            );

}


/* ============================================================
   REFRESH
============================================================ */

async function refreshAll() {

    await loadDashboard();


    if (currentPage === "nodes") {
        await loadNodes();
    }

    else if (currentPage === "testing") {
        await loadTesting();
    }

    else if (currentPage === "failures") {
        await loadFailures();
    }

    else if (currentPage === "logs") {
        await loadLogs();
    }

    else if (currentPage === "history") {
        await loadHistory();
    }

}


/* ============================================================
   INIT
============================================================ */

async function init() {

    setupNavigation();

    setupButtons();

    setupLogFilters();

    setupSearch();

    setupSettings();


    await setupEnvironmentSelector();


    document
        .getElementById(
            "default-environment"
        )
        .value =
        currentEnvironment;


    try {

        await refreshAll();

    }

    catch (error) {

        console.error(error);

        showToast(
            "Backend is not reachable. Start Uvicorn first.",
            "error"
        );

    }

}


document.addEventListener(
    "DOMContentLoaded",
    init
);