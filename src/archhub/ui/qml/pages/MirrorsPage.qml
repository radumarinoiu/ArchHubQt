import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Pane {
    id: root

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Label {
            text: qsTr("Mirrors")
            font.bold: true
        }
        Label {
            text: qsTr("Not implemented yet. This page will provide a small UI for reflector.")
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            color: palette.mid
        }
    }
}
