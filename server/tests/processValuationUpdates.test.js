const amqp = require("amqplib");
const pubsub = require("../src/pubsub");
const processValuationUpdates = require("../src/processValuationUpdates");

jest.mock("amqplib");
jest.mock("../src/pubsub");

describe("processValuationUpdates", () => {
  let connectionMock, channelMock, consumeMock;

  beforeAll(async () => {
    connectionMock = {
      createChannel: jest.fn(),
    };
    channelMock = {
      assertQueue: jest.fn(),
      consume: jest.fn(),
      ack: jest.fn(),
    };
    consumeMock = jest.fn();

    amqp.connect.mockResolvedValue(connectionMock);
    connectionMock.createChannel.mockResolvedValue(channelMock);
    channelMock.consume.mockImplementation((queue, onMessage) => {
      consumeMock = onMessage;
    });

    await processValuationUpdates();
  });

  it("should process messages from the queue", async () => {
    const testMessage = {
      content: Buffer.from(
        JSON.stringify({
          valuation: 42,
          taskId: "1",
          walletAddress: "0x123",
          folderPath: "/test/path",
        })
      ),
    };

    consumeMock(testMessage);

    expect(pubsub.publish).toHaveBeenCalledWith("TASK_UPDATED_/test/path", {
      taskUpdated: {
        valuation: 42,
        status: "Completed",
        taskId: "1",
        walletAddress: "0x123",
        folderPath: "/test/path",
      },
    });
    expect(channelMock.ack).toHaveBeenCalledWith(testMessage);
  });
});
