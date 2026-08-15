/*
 * ============================================================
 * ATELIIER FHM GLOBAL NOTIFICATION SHELL
 * ============================================================
 *
 * This module owns the application's notification UI.
 *
 * Future modules should create notifications through the
 * notification service. They should NOT create their own
 * notification bells, banners, sounds or notification counts.
 *
 * ============================================================
 */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        /*
         * ========================================================
         * SHELL DISCOVERY
         * ========================================================
         */

        const shell =
            document.getElementById(
                "global-notification-shell"
            );

        if (!shell) {
            return;
        }

        const authenticated =
            shell.dataset.authenticated === "true";

        if (!authenticated) {
            return;
        }


        const toggle =
            document.getElementById(
                "notification-toggle"
            );

        const menu =
            document.getElementById(
                "notification-menu"
            );

        const count =
            shell.querySelector(
                ".notification-count"
            );

        const items =
            document.getElementById(
                "notification-items"
            );

        const bannerContainer =
            document.getElementById(
                "notification-banner-container"
            );

        const markAllButton =
            document.getElementById(
                "notification-mark-all"
            );


        /*
         * ========================================================
         * INTERNAL STATE
         * ========================================================
         */

        let knownNotificationIds =
            new Set();

        let initialized = false;

        let audioContext = null;


        /*
         * ========================================================
         * ATELIIER FHM NOTIFICATION SOUND
         * ========================================================
         *
         * The sound is generated internally with Web Audio.
         *
         * There is no sound selector and no external audio file.
         *
         * Browser autoplay policies require a user interaction
         * before audio can normally be played.
         * ========================================================
         */

        function unlockAudio() {

            if (!audioContext) {

                const AudioContextClass =
                    window.AudioContext ||
                    window.webkitAudioContext;

                if (!AudioContextClass) {
                    return;
                }

                audioContext =
                    new AudioContextClass();

            }


            if (
                audioContext.state ===
                "suspended"
            ) {

                audioContext.resume().catch(
                    function () {
                        /*
                         * Browser audio permission may still be
                         * pending. A later user interaction will
                         * attempt the unlock again.
                         */
                    }
                );

            }

        }


        function playNotificationSound() {

            if (!audioContext) {
                return;
            }

            if (
                audioContext.state !==
                "running"
            ) {
                return;
            }


            const now =
                audioContext.currentTime;


            /*
             * Ateliier FHM notification motif:
             *
             * 880Hz → 1174.66Hz → 987.77Hz
             *
             * This is the application's fixed notification
             * signature.
             */

            const notes = [
                {
                    frequency: 880,
                    start: 0,
                    duration: 0.10
                },
                {
                    frequency: 1174.66,
                    start: 0.11,
                    duration: 0.10
                },
                {
                    frequency: 987.77,
                    start: 0.22,
                    duration: 0.16
                }
            ];


            notes.forEach(
                function (note) {

                    const oscillator =
                        audioContext.createOscillator();

                    const gain =
                        audioContext.createGain();


                    oscillator.type =
                        "sine";

                    oscillator.frequency.value =
                        note.frequency;


                    gain.gain.setValueAtTime(
                        0.0001,
                        now + note.start
                    );

                    gain.gain.exponentialRampToValueAtTime(
                        0.08,
                        now +
                        note.start +
                        0.015
                    );

                    gain.gain.exponentialRampToValueAtTime(
                        0.0001,
                        now +
                        note.start +
                        note.duration
                    );


                    oscillator.connect(gain);

                    gain.connect(
                        audioContext.destination
                    );


                    oscillator.start(
                        now + note.start
                    );

                    oscillator.stop(
                        now +
                        note.start +
                        note.duration +
                        0.01
                    );

                }
            );

        }


        /*
         * ========================================================
         * AUDIO UNLOCK
         * ========================================================
         */

        document.addEventListener(
            "click",
            unlockAudio,
            {
                passive: true
            }
        );

        document.addEventListener(
            "touchstart",
            unlockAudio,
            {
                passive: true
            }
        );


        /*
         * ========================================================
         * COUNT
         * ========================================================
         */

        function updateCount(
            unreadCount
        ) {

            if (!count) {
                return;
            }


            const numericCount =
                Number(unreadCount) || 0;


            if (numericCount <= 0) {

                count.textContent = "";

                count.classList.remove(
                    "has-notifications"
                );

                count.setAttribute(
                    "aria-label",
                    "No unread notifications"
                );

                return;
            }


            count.textContent =
                numericCount > 99
                    ? "99+"
                    : String(numericCount);


            count.classList.add(
                "has-notifications"
            );

            count.setAttribute(
                "aria-label",
                `${numericCount} unread notifications`
            );

        }


        /*
         * ========================================================
         * ESCAPE HTML
         * ========================================================
         *
         * Notification content comes from database data.
         * Never inject notification text into HTML unescaped.
         * ========================================================
         */

        function escapeHtml(
            value
        ) {

            const element =
                document.createElement(
                    "div"
                );

            element.textContent =
                value || "";

            return element.innerHTML;

        }


        /*
         * ========================================================
         * NOTIFICATION ITEM
         * ========================================================
         */

        function renderNotifications(
            notifications
        ) {

            if (!items) {
                return;
            }


            if (!notifications.length) {

                items.innerHTML = `
                    <div class="notification-empty">
                        <span class="notification-empty-icon">
                            🔔
                        </span>

                        <span>
                            No notifications yet.
                        </span>
                    </div>
                `;

                return;
            }


            items.innerHTML =
                notifications
                    .map(
                        function (notification) {

                            const unreadClass =
                                notification.is_read
                                    ? ""
                                    : " unread";


                            const destination =
                                notification.link ||
                                "/notifications/all";


                            return `
                                <div
                                    class="
                                        notification-item
                                        ${unreadClass}
                                    "
                                    data-notification-id="${escapeHtml(
                                        notification.id
                                    )}"
                                >

                                    <div
                                        class="
                                            notification-item-content
                                        "
                                    >

                                        <strong>
                                            ${escapeHtml(
                                                notification.title
                                            )}
                                        </strong>

                                        <span>
                                            ${escapeHtml(
                                                notification.message
                                            )}
                                        </span>

                                    </div>


                                    <a
                                        href="${escapeHtml(
                                            destination
                                        )}"
                                        class="
                                            notification-item-link
                                        "
                                    >
                                        View
                                    </a>

                                </div>
                            `;

                        }
                    )
                    .join("");


            attachNotificationItemHandlers();

        }


        function attachNotificationItemHandlers() {

            items
                .querySelectorAll(
                    ".notification-item[data-notification-id]"
                )
                .forEach(
                    function (item) {

                        item.addEventListener(
                            "click",
                            function (event) {

                                const notificationId =
                                    item.dataset.notificationId;


                                markAsRead(
                                    notificationId
                                );


                                const link =
                                    event.target.closest(
                                        "a"
                                    );


                                if (link) {
                                    return;
                                }


                                if (
                                    !item.querySelector(
                                        "a"
                                    )
                                ) {
                                    return;
                                }

                            }
                        );

                    }
                );

        }


        /*
         * ========================================================
         * BANNER
         * ========================================================
         */

        function showBanner(
            notification,
            playSound
        ) {

            if (!bannerContainer) {
                return;
            }


            const banner =
                document.createElement(
                    "div"
                );

            banner.className =
                "notification-banner";


            banner.dataset.notificationId =
                String(
                    notification.id
                );


            const destination =
                notification.link ||
                "/notifications/all";


            banner.innerHTML = `
                <div
                    class="notification-banner-icon"
                >
                    🔔
                </div>

                <div
                    class="notification-banner-content"
                >

                    <strong>
                        ${escapeHtml(
                            notification.title
                        )}
                    </strong>

                    <span>
                        ${escapeHtml(
                            notification.message
                        )}
                    </span>

                </div>

                <a
                    href="${escapeHtml(
                        destination
                    )}"
                    class="notification-banner-view"
                >
                    View
                </a>

                <button
                    type="button"
                    class="notification-banner-close"
                    aria-label="Close notification"
                >
                    ×
                </button>
            `;


            bannerContainer.appendChild(
                banner
            );


            requestAnimationFrame(
                function () {

                    banner.classList.add(
                        "active"
                    );

                }
            );


            const close =
                banner.querySelector(
                    ".notification-banner-close"
                );


            close.addEventListener(
                "click",
                function () {

                    removeBanner(
                        banner
                    );

                }
            );


            setTimeout(
                function () {

                    removeBanner(
                        banner
                    );

                },
                7000
            );


            if (playSound) {
                playNotificationSound();
            }

        }


        function removeBanner(
            banner
        ) {

            if (!banner) {
                return;
            }


            banner.classList.remove(
                "active"
            );


            setTimeout(
                function () {

                    banner.remove();

                },
                300
            );

        }


        /*
         * ========================================================
         * LOAD NOTIFICATIONS
         * ========================================================
         */

        async function loadNotifications(
            showNewNotifications
        ) {

            try {

                const response =
                    await fetch(
                        "/notifications/",
                        {
                            method: "GET",
                            headers: {
                                "Accept":
                                    "application/json"
                            },
                            credentials:
                                "same-origin",
                            cache:
                                "no-store"
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        `Notification API returned ${response.status}`
                    );

                }


                const data =
                    await response.json();


                const notifications =
                    Array.isArray(
                        data.notifications
                    )
                        ? data.notifications
                        : [];


                updateCount(
                    data.unread_count
                );


                renderNotifications(
                    notifications
                );


                const currentIds =
                    new Set(
                        notifications.map(
                            function (
                                notification
                            ) {

                                return String(
                                    notification.id
                                );

                            }
                        )
                    );


                if (
                    initialized &&
                    showNewNotifications
                ) {

                    notifications
                        .filter(
                            function (
                                notification
                            ) {

                                return (
                                    !notification.is_read &&
                                    !knownNotificationIds.has(
                                        String(
                                            notification.id
                                        )
                                    )
                                );

                            }
                        )
                        .reverse()
                        .forEach(
                            function (
                                notification
                            ) {

                                showBanner(
                                    notification,
                                    true
                                );

                            }
                        );

                }


                knownNotificationIds =
                    currentIds;

                initialized = true;


            } catch (error) {

                console.error(
                    "Ateliier FHM notification shell:",
                    error
                );


                if (items) {

                    items.innerHTML = `
                        <div
                            class="notification-empty notification-error"
                        >
                            <span>
                                Unable to load notifications.
                            </span>
                        </div>
                    `;

                }

            }

        }


        /*
         * ========================================================
         * MARK ONE AS READ
         * ========================================================
         */

        async function markAsRead(
            notificationId
        ) {

            try {

                const response =
                    await fetch(
                        `/notifications/${notificationId}/read`,
                        {
                            method: "POST",
                            headers: {
                                "Accept":
                                    "application/json"
                            },
                            credentials:
                                "same-origin"
                        }
                    );


                if (!response.ok) {
                    return;
                }


                const data =
                    await response.json();


                updateCount(
                    data.unread_count
                );


            } catch (error) {

                console.warn(
                    "Unable to mark notification as read:",
                    error
                );

            }

        }


        /*
         * ========================================================
         * MARK ALL AS READ
         * ========================================================
         */

        if (markAllButton) {

            markAllButton.addEventListener(
                "click",
                async function () {

                    try {

                        const response =
                            await fetch(
                                "/notifications/read-all",
                                {
                                    method: "POST",
                                    headers: {
                                        "Accept":
                                            "application/json"
                                    },
                                    credentials:
                                        "same-origin"
                                }
                            );


                        if (!response.ok) {
                            return;
                        }


                        updateCount(0);

                        await loadNotifications(
                            false
                        );


                    } catch (error) {

                        console.warn(
                            "Unable to mark all notifications as read:",
                            error
                        );

                    }

                }
            );

        }


        /*
         * ========================================================
         * DROPDOWN
         * ========================================================
         */

        if (
            toggle &&
            menu
        ) {

            toggle.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();

                    unlockAudio();

                    const active =
                        menu.classList.toggle(
                            "active"
                        );


                    toggle.setAttribute(
                        "aria-expanded",
                        active
                            ? "true"
                            : "false"
                    );

                }
            );


            menu.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();

                }
            );


            document.addEventListener(
                "click",
                function () {

                    menu.classList.remove(
                        "active"
                    );

                    toggle.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }
            );

        }


        /*
         * ========================================================
         * INITIAL LOAD
         * ========================================================
         */

        loadNotifications(
            false
        );


        /*
         * ========================================================
         * POLLING
         * ========================================================
         *
         * Poll every 30 seconds.
         *
         * This gives the application a global notification layer
         * without prematurely introducing WebSocket infrastructure.
         * ========================================================
         */

        setInterval(
            function () {

                loadNotifications(
                    true
                );

            },
            30000
        );


    }
);
