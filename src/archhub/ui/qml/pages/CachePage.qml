import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Pane {
    id: root

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Label {
            text: qsTr("Cache statistics")
            font.bold: true
        }
        GridLayout {
            columns: 2
            rowSpacing: 4
            Label { text: qsTr("Total size:") }
            Label { text: appModel ? formatSize(appModel.getCacheStatsSize()) : "0 B" }
            Label { text: qsTr("Package count:") }
            Label { text: appModel ? appModel.getCacheStatsCount() : 0 }
        }

        Button {
            text: qsTr("Quick Clean")
            enabled: false
            ToolTip.visible: hovered
            ToolTip.text: qsTr("Not implemented yet")
        }
        Button {
            text: qsTr("Selective Clean")
            enabled: false
            ToolTip.visible: hovered
            ToolTip.text: qsTr("Not implemented yet")
        }
    }

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + " B"
        if (bytes < 1024*1024) return (bytes / 1024).toFixed(1) + " KiB"
        return (bytes / (1024*1024)).toFixed(1) + " MiB"
    }

    Component.onCompleted: if (appModel) appModel.refreshCacheStats()
}
