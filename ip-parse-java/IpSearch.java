package qqzeng.ip;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
/**
 * ����һ���ļ��ṹ �����ܽ���IP���ݿ� qqzeng-ip.dat
 * ���룺UTF8 �ֽ���Little-Endian
 * For detailed information and guide: http://qqzeng.com/
 * @author qqzeng-ip �� 2015-08-01
 */
public class IpSearch {

	private static IpSearch instance = null;

	private byte[] data;

	private HashMap<Integer, PrefixIndex> prefixMap;

	private long firstStartIpOffset;// ��������һ����λ��
	// private int lastStartIpOffset;//���������һ����λ��
	private long prefixStartOffset;// ǰ׺����һ������λ��
	private long prefixEndOffset;// ǰ׺�����һ������λ��
	// private int ipCount; //ip������
	private long prefixCount; // ǰ׺����

	public IpSearch() {

		Path path = Paths
				.get("C:/qqzeng-ip-java/bin/qqzeng-ip.dat");

		try {
			data = Files.readAllBytes(path);
		} catch (IOException e) {
			e.printStackTrace();
		}

		firstStartIpOffset = BytesToLong(data[0], data[1], data[2], data[3]);
		// lastStartIpOffset = BytesToLong(data[4], data[5], data[6], data[7]);
		prefixStartOffset = BytesToLong(data[8], data[9], data[10], data[11]);
		prefixEndOffset = BytesToLong(data[12], data[13], data[14], data[15]);

		// ipCount = (lastStartIpOffset - firstStartIpOffset) / 12 + 1; //��������ÿ��
		// 12�ֽ�
		prefixCount = (prefixEndOffset - prefixStartOffset) / 9 + 1; // ǰ׺����ÿ��
		// 9�ֽ�

		// ��ʼ��ǰ׺��Ӧ����������
		byte[] indexBuffer = Arrays.copyOfRange(data, (int) prefixStartOffset,(int) prefixEndOffset + 9);
		prefixMap = new HashMap<Integer, PrefixIndex>();
		for (int k = 0; k < prefixCount; k++) {
			int i = k * 9;
			int prefix = (int) (indexBuffer[i] & 0xFFL);

			PrefixIndex pf = new PrefixIndex();
			pf.start_index = BytesToLong(indexBuffer[i + 1],indexBuffer[i + 2], indexBuffer[i + 3], indexBuffer[i + 4]);
			pf.end_index = BytesToLong(indexBuffer[i + 5], indexBuffer[i + 6],indexBuffer[i + 7], indexBuffer[i + 8]);
			prefixMap.put(prefix, pf);

		}

	}

	public synchronized static IpSearch getInstance() {
		if (null == instance)
			instance = new IpSearch();
		return instance;
	}

	public String Get(String ip) {
		String[] ips = ip.split("\\.");
		int prefix = Integer.valueOf(ips[0]);
		long intIP = ipToLong(ip);

		long high = 0;
		long low = 0;

		if (prefixMap.containsKey(prefix)) {
			low = prefixMap.get(prefix).start_index;
			high = prefixMap.get(prefix).end_index;

		} else {
			return "";
		}
		
		long my_index = low == high ? low : BinarySearch(low, high, intIP);

		IpIndex ipindex = new IpIndex();
		GetIndex((int) my_index, ipindex);

		if ((ipindex.startip <= intIP) && (ipindex.endip >= intIP)) {
			return GetLocal(ipindex.local_offset, ipindex.local_length);
		} else {
			return "";
		}

	}

	// / <summary>
	// / ���ֱƽ��㷨
	// / </summary>
	public long BinarySearch(long low, long high, long k) {
		long M = 0;
		while (low <= high) {
			long mid = (low + high) / 2;

			long endipNum = GetEndIp(mid);
			if (endipNum >= k) {
				M = mid;
				if (mid == 0) {
					break; // ��ֹ���
				}
				high = mid - 1;
			} else
				low = mid + 1;
		}
		return M;
	}

	// / <summary>
	// / ������������
	// / </summary>
	// / <param name="left">ip��left������</param>
	private void GetIndex(int left, IpIndex ipindex) {
		int left_offset = (int) firstStartIpOffset + (left * 12);
		ipindex.startip = BytesToLong(data[left_offset], data[1 + left_offset],data[2 + left_offset], data[3 + left_offset]);
		ipindex.endip = BytesToLong(data[4 + left_offset],data[5 + left_offset], data[6 + left_offset],data[7 + left_offset]);
		ipindex.local_offset = (int) BytesToLong3(data[8 + left_offset],data[9 + left_offset], data[10 + left_offset]);
		ipindex.local_length = (int) data[11 + left_offset];
	}

	// / <summary>
	// / ֻ��ȡ����ip����ֵ
	// / </summary>
	// / <param name="left">��������left������</param>
	// / <returns>���ؽ���ip����ֵ</returns>
	private long GetEndIp(long left) {
		int left_offset = (int) firstStartIpOffset + (int) (left * 12);
		return BytesToLong(data[4 + left_offset], data[5 + left_offset],data[6 + left_offset], data[7 + left_offset]);

	}

	// / <summary>
	// / ���ص�ַ��Ϣ
	// / </summary>
	// / <param name="local_offset">��ַ��Ϣ����λ��</param>
	// / <param name="local_length">��ַ��Ϣ��������</param>
	// / <returns></returns>
	private String GetLocal(int local_offset, int local_length) {
		byte[] bytes = new byte[local_length];
		bytes = Arrays.copyOfRange(data, local_offset, local_offset	+ local_length);
		return new String(bytes, StandardCharsets.UTF_8);

	}

	// / <summary>
	// / �ֽ�ת���� С����
	// / </summary>
	private long BytesToLong(byte a, byte b, byte c, byte d) {
		return (a & 0xFFL) | ((b << 8) & 0xFF00L) | ((c << 16) & 0xFF0000L)	| ((d << 24) & 0xFF000000L);

	}

	private long BytesToLong3(byte a, byte b, byte c) {
		return (a & 0xFFL) | ((b << 8) & 0xFF00L) | ((c << 16) & 0xFF0000L);

	}

	public long ipToLong(String ip) {
		String[] quads = ip.split("\\.");
		long result = 0;
		result += Integer.parseInt(quads[3]);
		result += Long.parseLong(quads[2]) << 8L;
		result += Long.parseLong(quads[1]) << 16L;
		result += Long.parseLong(quads[0]) << 24L;
		return result;
	}

	public static void main(String[] args) {

		IpSearch finder = IpSearch.getInstance();

		String ip = "210.51.200.123";
		String result = finder.Get(ip);
		System.out.println(ip);
		System.out.println(result);

		/*
		 * 1.197.224.9 ����|�й�|����|�ܿ�|��ˮ|����|411623|China|CN|114.60604|33.53912
		 */

	}
}