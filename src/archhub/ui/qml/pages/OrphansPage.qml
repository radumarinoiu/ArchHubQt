import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Pane {
    id: root

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        Label {
            text: qsTr("Orphaned packages (no longer required by any other package)")
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            ListView {
                model: orphanModel
                delegate: ItemDelegate {
                    width: ListView.view ? ListView.view.width - 4 : 200
                    text: model.name + " " + model.version
                }
            }
        }

        RowLayout {
            Button {
                text: qsTr("Remove Selected")
                enabled: false
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Not implemented yet")
            }
            Button {
                text: qsTr("Remove All")
                enabled: false
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Not implemented yet")
            }
        }
    }

    Component.onCompleted: if (appModel) appModel.refreshOrphans()
}
