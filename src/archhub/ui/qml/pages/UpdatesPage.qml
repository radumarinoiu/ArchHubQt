import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Pane {
    id: root

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            Layout.margins: 8
            Label { text: qsTr("Include AUR updates") }
            Switch {
                checked: appModel ? appModel.updatesIncludeAur : false
                onCheckedChanged: if (appModel) appModel.updatesIncludeAur = checked
            }
        }

        Label {
            text: qsTr("Total download size: ") + (appModel ? formatSize(appModel.getTotalDownloadSize()) : "0 B")
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            ListView {
                model: updateModel
                delegate: ItemDelegate {
                    width: ListView.view ? ListView.view.width - 4 : 200
                    text: model.name + " " + model.currentVersion + " → " + model.newVersion
                }
            }
        }

        RowLayout {
            Button {
                text: qsTr("Update Selected")
                enabled: false
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Not implemented yet")
            }
            Button {
                text: qsTr("Update All")
                enabled: false
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Not implemented yet")
            }
        }

        Label {
            text: qsTr("Arch News preview")
            font.bold: true
        }
        Label {
            text: qsTr("(Arch News preview not implemented)")
            color: palette.mid
        }
    }

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + " B"
        if (bytes < 1024*1024) return (bytes / 1024).toFixed(1) + " KiB"
        return (bytes / (1024*1024)).toFixed(1) + " MiB"
    }

    Component.onCompleted: if (appModel) appModel.refreshUpdatesList()
}
