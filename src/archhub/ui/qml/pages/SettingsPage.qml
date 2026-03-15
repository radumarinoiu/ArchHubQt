import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Pane {
    id: root

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        Label {
            text: qsTr("AUR Helpers")
            font.bold: true
        }
        Repeater {
            model: appModel ? appModel.getAvailableHelperIds() : []
            delegate: RowLayout {
                CheckBox {
                    checked: appModel ? appModel.getHelperEnabled(modelData) : false
                    onCheckedChanged: if (appModel) appModel.setHelperEnabled(modelData, checked)
                    text: modelData
                }
            }
        }

        Label {
            text: qsTr("Parallel downloads")
            font.bold: true
        }
        SpinBox {
            from: 0
            to: 20
            value: 0
            editable: true
            ToolTip.text: qsTr("0 = use pacman default. Not persisted yet.")
        }

        Label {
            text: qsTr("Shortcuts")
            font.bold: true
        }
        Button {
            text: qsTr("Open Pacman Config")
            onClicked: Qt.openUrlExternally("file://" + (appModel ? appModel.getPacmanConfPath() : ""))
        }
        Button {
            text: qsTr("Open Mirror List")
            onClicked: Qt.openUrlExternally("file://" + (appModel ? appModel.getMirrorListPath() : ""))
        }
    }
}
